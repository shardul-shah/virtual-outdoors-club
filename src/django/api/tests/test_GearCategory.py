from django.test import TestCase
from ..models import GearCategory
from rest_framework.test import APIRequestFactory

'''
should have a test to ensure that all input and editing to category names
are input as lowercase
'''


class GearCategoryTestCase(TestCase):

    # Create test data and save primary key of all objects
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        GearCategory.objects.create(name="Book")
        GearCategory.objects.create(name="Water Bottle")
        self.client = APIRequestFactory

    def test_get(self):
        response = self.client.get("/api/gear/categories/", content_type="application/json").data['data']
        # Test json response
        expectedResponse = [{"name": "Book"}, {'name': "Water Bottle"}]
        self.assertEqual(response, expectedResponse)

    def test_post(self):
        request = {"name": "Tent"}

        # Test the post request
        response = self.client.post("/api/gear/categories/", request, content_type='application/json').data
        self.assertEqual(response, request)
                                                                        
        # Make sure the post (addition of gear category) was saved to the db
        response = self.client.get("/api/gear/categories").data['data']
        correctReturn = [{"name": "Book"}, {'name': "Water Bottle"}, {"name": "Tent"}]
        self.assertEqual(response, correctReturn)
    
    def test_delete(self):
        response = self.client.delete("/api/gear/categories?name=Book", content_type="application/json").data
        self.assertEqual(response, {"message": "Deleted the category: 'Book'"})

        response = self.client.get("/api/gear/categories").data['data']
        self.assertEqual(response, [{'name': "Water Bottle"}])

    def test_delete_does_not_exist(self):
        name = "somecategorythatshouldneverexist"
        response = self.client.delete("/api/gear/categories?name=" + name, content_type="application/json").data
        self.assertEqual(response, {"message": "The gear category '" + name + "' does not exist so it cannot be deleted."})
