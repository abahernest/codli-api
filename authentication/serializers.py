from django.utils import timezone
import re
from rest_framework import serializers
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed, ParseError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from users.models import User, EmailVerification, USER_ROLES


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=68, write_only=True)
    role = serializers.IntegerField(min_value=0, max_value=1, write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = ['password', 'email', 'role']

    def validate(self, attrs):
        password = attrs.get('password', '')
        role = attrs.get('role', '')
        email = attrs.get('email', '')

        if not email:
            raise serializers.ValidationError("email is required")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise serializers.ValidationError("invalid email address")
        
        if role not in [0, 1]:
            raise serializers.ValidationError("role is required")   
        
        if re.search('[A-Z]', password) is None:
            raise serializers.ValidationError("password must contain One Uppercase Alphabet")

        if re.search('[a-z]', password) is None:
            raise serializers.ValidationError("password must contain One Lowercase Alphabet")

        if re.search('[0-9]', password) is None:
            raise serializers.ValidationError("password must contain One Numeric Character")

        if re.search(r"[@$!%*#?&]", password) is None:
            raise serializers.ValidationError("password must contain One Special Character")


        attrs['role'] = USER_ROLES[role][0]

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=6, min_length=6, write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = ['token', 'email']

    def validate(self, attrs):
        email = attrs.get('email', '')
        token = attrs.get('token', '')

        users = User.objects.filter(email=email)
        if len(users) <= 0:
            raise ParseError('user not found')

        user = users[0]
        verificationObj = EmailVerification.objects.filter(user=user)

        if len(verificationObj) <= 0:
            raise ParseError('user not found')

        verificationObj = verificationObj[0]
        if verificationObj.token != token:
            raise ParseError('wrong token')

        if verificationObj.is_verified:
            raise ParseError('token expired')

        if verificationObj.token_expiry < timezone.now():
            raise ParseError('token expired')

        verificationObj.is_verified = True
        verificationObj.token_expiry = timezone.now()
        verificationObj.save()
        user.is_verified = True
        user.save()

        return True


class ResendVerificationMailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')

        user = User.objects.filter(email=email, is_verified=False).first()
        if user:
            verification_obj = EmailVerification.objects.filter(user=user, is_verified=False).first()
            return verification_obj

        return False


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=8, write_only=True)
    display_name = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    role = serializers.CharField(
        max_length=255, min_length=3, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'tokens', 'display_name', 'role', 'id', 'signup_checklist']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('please verify your email')

        return {
            'email': user.email,
            'display_name': user.display_name,
            'role': user.role,
            'tokens': user.tokens,
            'id': user.id,
            'signup_checklist': user.signup_checklist,
            }


class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    token = serializers.CharField(min_length=1, read_only=True)
    uid64 = serializers.CharField(min_length=1, read_only=True)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email', 'uid64', 'token']

    def validate(self, attrs):
        email = attrs.get('email', '')
        users = User.objects.filter(email=email)

        if len(users) <= 0:
            # if user account not found, don't throw error
            return False

        user = users[0]

        # encode userId as base64 uuid
        uid64 = urlsafe_base64_encode(smart_bytes(user.id))

        # generate reset token
        token = PasswordResetTokenGenerator().make_token(user)

        return {"uid64": uid64, "token": token, "email": user.email}


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uid64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uid64']

    def validate(self, attrs):

        password = attrs.get('password')
        token = attrs.get('token')
        uid64 = attrs.get('uid64')

        # Decode base64 string
        try:
            id = force_str(urlsafe_base64_decode(uid64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)

        # Validate password

        if re.search('[A-Z]', password) is None:
            raise serializers.ValidationError(
                "Password must contain One Uppercase Alphabet")

        if re.search('[a-z]', password) is None:
            raise serializers.ValidationError(
                "Password must contain One Lowercase Alphabet")

        if re.search('[0-9]', password) is None:
            raise serializers.ValidationError(
                "Password must contain One Numeric Character")

        if re.search(r"[@$!%*#?&]", password) is None:
            raise serializers.ValidationError(
                "Password must contain One Special Character")

        # Update password
        user.set_password(password)
        user.save()

        return (user)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    new_password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)

    class Meta:
        fields = ['current_password', 'new_password']

    def validate(self, attrs):

        user = self.instance
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')

        # validate old password
        isCorrectPassword = user.check_password(current_password)
        if not isCorrectPassword :
            raise serializers.ValidationError("current password not correct")
        # Validate new password

        if re.search('[A-Z]', new_password) is None:
            raise serializers.ValidationError(
                "Password must contain One Uppercase Alphabet")

        if re.search('[a-z]', new_password) is None:
            raise serializers.ValidationError(
                "Password must contain One Lowercase Alphabet")

        if re.search('[0-9]', new_password) is None:
            raise serializers.ValidationError(
                "Password must contain One Numeric Character")

        if re.search(r"[@$!%*#?&]", new_password) is None:
            raise serializers.ValidationError(
                "Password must contain One Special Character")

        user.set_password(new_password)
        user.save()
        return user
