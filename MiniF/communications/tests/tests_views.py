from django.test import TestCase
from django.urls import reverse


class CommunicationsViewsTest(TestCase):
    def test_index_view(self):
        """Checks that the index view returns status 200."""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_room_view(self):
        """Checks that the room view returns status 200 and passes room_name."""
        response = self.client.get(reverse("room", args=["testroom"]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"testroom", response.content)