from django.test import TestCase
from services.mgmt import get_available_services, available_services


class ServicesManagement(TestCase):

    def test_get_available_services(self):

        # Check that all services are returned by get_available_services() when no further parameters are given
        for service in available_services:
            self.assertIn(service, get_available_services())

        # Check that using an include filter only returns included service
        self.assertIn(available_services[0].name, get_available_services(include=[available_services[0].name])[0].name)
        self.assertEquals(len(get_available_services(include=[available_services[0].name])), 1)

        # Check that using an empty list include filter returns no services
        self.assertEquals(len(get_available_services(include=[])), 0)

        # Check that using an empty list for exclude has no effect
        self.assertEquals(len(get_available_services(exclude=[])), len(get_available_services()))

        # Check that excluding a services removes it from the list
        self.assertNotIn(available_services[0], get_available_services(exclude=[available_services[0].name]))

        # Check filtering by component
        self.assertEquals(len(get_available_services(component="nonExistingComponent")), 0)
        components = list()
        for service in available_services:
            components += service.implemented_components
        component = components[0]
        count = components.count(component)
        self.assertEquals(len(get_available_services(component=component)), count)
