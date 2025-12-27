from rest_framework import serializers
from .models import ContactMessage
import re

class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Serializer to validate and serialize contact form data
    """
    
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_name(self, value):
        """Validate name - no numbers or special chars"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long")
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("Name should not contain numbers")
        return value.strip()
    
    def validate_email(self, value):
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Enter a valid email address")
        return value.lower()
    
    def validate_phone(self, value):
        """Validate phone number - accepts 10-15 digits"""
        phone_digits = ''.join(filter(str.isdigit, value))
        if len(phone_digits) < 10 or len(phone_digits) > 15:
            raise serializers.ValidationError("Phone number must be 10-15 digits")
        return value
    
    def validate_message(self, value):
        """Validate message - minimum length"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters")
        return value.strip()
    
    def validate_subject(self, value):
        """Validate subject is one of the allowed choices"""
        valid_choices = ['paper_submission', 'general_inquiry', 'buy_journal']
        if value not in valid_choices:
            raise serializers.ValidationError(f"Subject must be one of {valid_choices}")
        return value
