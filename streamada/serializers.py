from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


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


        #E-mail send
        send_mail(
            subject='Please Confirm your E-mail',
            message=f'Hallo {user.first_name} {user.last_name},\nPlease click the link below to activate your account:\n{activation_link}',
            from_email='noreply@streamada.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user
