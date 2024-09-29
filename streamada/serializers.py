from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Password do not match")
        return data
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        print("Serializer context:", self.context)
        request = self.context.get('request', None)
        if not request:
            raise Exception("Request is not in serializer context")
        
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['email'],
            is_active=False
        )
        user.set_password(validated_data['password'])  
        user.save()
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        activation_link = f"{self.context['request'].scheme}://{self.context['request'].get_host()}/api/activate/{uid}/{token}/"

        subject = 'Please Confirm your E-mail'
        from_email = 'noreply@streamada.com'
        recipient_list = [user.email]

        html_message = render_to_string('send_activation_link.html', {
            'user': user,
            'activation_link': activation_link
        })

        email = EmailMultiAlternatives(
            subject=subject,
            body=f'Hallo {user.first_name} {user.last_name},\nPlease click the link below to activate your account:\n{activation_link}',
            from_email=from_email,
            to=recipient_list
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User dosen't exist.")
        
        if not user.is_active:
            raise serializers.ValidationError("Acount not activated, check your email.")
        
        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("password is wrong.")
        
        data['user'] = user
        return data 