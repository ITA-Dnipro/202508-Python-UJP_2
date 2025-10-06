from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from users.permissions import IsStartupRole, IsInvestorRole, CustomPermission, _get_role_from_request
from users.models import UserProfile
from profiles.models import Industry, StartupProfile, InvestorProfile
from unittest.mock import Mock


class PermissionsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserProfile.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpassword123"
        )
        self.industry = Industry.objects.create(industry_name="Technology")

    def test_get_role_from_request_with_token(self):
        """Test getting role from JWT token"""
        refresh = RefreshToken.for_user(self.user)
        refresh['role'] = 'startup'
        access = refresh.access_token
        
        request = self.factory.get('/')
        request.auth = access
        
        role = _get_role_from_request(request)
        self.assertEqual(role, 'startup')

    def test_get_role_from_request_without_token(self):
        """Test getting role without token"""
        request = self.factory.get('/')
        mock_user = Mock()
        mock_user.is_authenticated = True
        mock_user.role = None
        request.user = mock_user
        
        role = _get_role_from_request(request)
        self.assertIsNone(role)

    def test_is_startup_role_permission_success(self):
        """Test IsStartupRole permission for startup role"""
        refresh = RefreshToken.for_user(self.user)
        refresh['role'] = 'startup'
        access = refresh.access_token
        
        request = self.factory.get('/')
        request.auth = access
        
        permission = IsStartupRole()
        self.assertTrue(permission.has_permission(request, None))

    def test_is_startup_role_permission_fail(self):
        """Test IsStartupRole permission denial for investor role"""
        refresh = RefreshToken.for_user(self.user)
        refresh['role'] = 'investor'
        access = refresh.access_token
        
        request = self.factory.get('/')
        request.auth = access
        
        permission = IsStartupRole()
        self.assertFalse(permission.has_permission(request, None))

    def test_is_investor_role_permission_success(self):
        """Test IsInvestorRole permission for investor role"""
        refresh = RefreshToken.for_user(self.user)
        refresh['role'] = 'investor'
        access = refresh.access_token
        
        request = self.factory.get('/')
        request.auth = access
        
        permission = IsInvestorRole()
        self.assertTrue(permission.has_permission(request, None))

    def test_custom_permission_authenticated_user(self):
        """Test CustomPermission for authenticated user"""
        request = self.factory.get('/')
        mock_user = Mock()
        mock_user.is_authenticated = True
        request.user = mock_user
        
        permission = CustomPermission()
        self.assertTrue(permission.has_permission(request, None))

    def test_custom_permission_unauthenticated_user(self):
        """Test CustomPermission for unauthenticated user"""
        request = self.factory.get('/')
        mock_user = Mock()
        mock_user.is_authenticated = False
        request.user = mock_user
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        permission = CustomPermission()
        self.assertFalse(permission.has_permission(request, None))