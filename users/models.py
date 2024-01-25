import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.exceptions import NotAcceptable
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

User=get_user_model()

TOKEN_LENGTH=6

class CreatedModified(models.Model):
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True) 

    class Meta:
        abstract=True
    
class PhoneNumber(CreatedModified):
    user=models.OneToOneField(User,related_name="phone",on_delete=models.CASCADE)
    phone_number=PhoneNumberField(unique=True)
    security_code=models.CharField(max_length=120)
    is_verified=models.BooleanField(default=False)
    sent=models.DateTimeField(null=True)

    

    class Meta:
        ordering=("-created_at",)
    
    def __str__(self) -> str:
        return self.phone_number.as_e164
    
    def generate_security_code(self):
        """
        Returns a random unique security code
        """
        
        token_length=getattr(settings,"TOKEN_LENGTH",TOKEN_LENGTH)
        return get_random_string(token_length,allowed_chars= "0123456789")
    
    def is_security_code_expired(self):
        expiration_date=self.sent + datetime.timedelta(
            minutes=settings.TOKEN_EXPIRE_MINUTES
        )
        
        return expiration_date<=timezone.now()


    
    def send_confirmation(self):
        twilio_account_sid=settings.TWILIO_ACCOUNT_SID
        twilio_auth_token=settings.TWILIO_AUTH_TOKEN
        twilio_phone_number=settings.TWILIO_PHONE_NUMBER

        self.security_code=self.generate_security_code()


        if not all([twilio_account_sid,twilio_auth_token,twilio_phone_number]):
            raise ValueError("All Twilio configuration parameters must be set: account SID, auth token, and phone number.")
        try:
            twilio_client=Client(twilio_account_sid,twilio_auth_token)
            twilio_client.messages.create(
                body=f"Your activation code is  {self.security_code}",
                to=str(self.phone_number),
                from_=twilio_phone_number
            )
            
            self.sent=timezone.now()
            self.save()
            return True
        except TwilioRestException as e:
            raise ValueError("Cannot connect with twilio")


    def check_verification(self, security_code):
        if (self.is_security_code_expired() or security_code!=self.security_code or self.is_verified ):
            raise NotAcceptable(_("Your security code is wrong, expired, or already verified"))
        
        self.is_verified=True
        self.save()
        return self.is_verified
    

class Profile(CreatedModified):
    user=models.OneToOneField(User,related_name="profile",on_delete=models.CASCADE)
    avatar=models.ImageField(upload_to="avatar",blank=True)
    bio=models.CharField(max_length=200,blank=True)

    class Meta:
        ordering=("-created_at",)
    
    def __str__(self):
        return self.user_get_full_name()
    
    

class Address(CreatedModified):
    
    BILLING="B"
    SHIPPING="S"

    ADDRESS_CHOICES=((BILLING,_("billing")),(SHIPPING,_("shipping")))

    user=models.ForeignKey(User,related_name="addresses",on_delete=models.CASCADE)
    address_type=models.CharField(max_length=1,choices=ADDRESS_CHOICES)
    default=models.BooleanField(default=False)
    country=CountryField()
    city=models.CharField(max_length=100)
    street_address=models.CharField(max_length=100)
    apartment_address=models.CharField(max_length=100)
    postal_code=models.CharField(max_length=20,blank=True)

    class Meta:
        ordering=("-created_at",)
    
    def __str__(self):
        return self.user.get_full_name()

        


        
        
        
        
        
        


# Create your models here.
