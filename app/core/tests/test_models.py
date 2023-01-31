"""
tests for models.
"""

from django.test import testcases
from django.contrib.auth import get_user_model


class ModelTests(testcases.TestCase):
    """
    test models.
    """

    def test_create_user_with_email_successful(self):
        """
        test creating a new user with an email is successful.
        """
        email = 'test@example.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        test the email for a new user is normalized.
        """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'test123')

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """
        test creating a new user without an email raises error.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        """
        test creating a new superuser.
        """
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
