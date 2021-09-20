import pytest
from django.urls import reverse, NoReverseMatch
from rest_framework import status

from house.models import RequiredVerification
from house.models.amenity import Amenity
from tests.factories.amenity_factory import AmenityCategoryFactory, AmenityFactory


class TestAmenityAPI:
    @pytest.fixture(autouse=True)
    def create_default_amenity_category(self, default_amenity_category):
        self.default_amenity_category = default_amenity_category

    @staticmethod
    def create_amenity_by_user(user):
        new_amenity = AmenityFactory(is_active=True)
        RequiredVerification(
            content_object=new_amenity,
            user=user,
        ).save()
        return new_amenity

    @pytest.mark.parametrize(
        'url_name,cat_cnt,am_cnt1,am_cnt2,am_cnt3',
        [
            ('amenity-list', 3, 10, 10, 1),
            ('amenity-for_house_list', 3, 2, 2, 1),
            ('amenity-for_house_space_list', 3, 3, 3, 1),
        ]
    )
    def test_list_success(self, db, authenticated_client, user, second_user,
                          url_name, cat_cnt, am_cnt1, am_cnt2, am_cnt3):
        """Test users can get list of amenities."""

        categories = [
            self.default_amenity_category,
            AmenityCategoryFactory(order=20),
            AmenityCategoryFactory(order=10),
        ]

        for category in categories:
            AmenityFactory.create_batch(2, category=category, is_active=True, is_available_for_house=True)
            AmenityFactory.create_batch(2, category=category, is_active=True, is_available_for_house=False)
            AmenityFactory.create_batch(3, category=category, is_active=True, is_available_for_house_kspace=True)
            AmenityFactory.create_batch(3, category=category, is_active=True, is_available_for_house_space=False)
            AmenityFactory.create_batch(5, category=category, is_active=False,
                                        is_available_for_house=True, is_available_for_house_space=True)

        user_amenity = self.create_amenity_by_user(user)
        second_user_amenity = self.create_amenity_by_user(second_user)  # noqa

        url = reverse(f'smp_api:{url_name}')
        # test without filtering
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == cat_cnt
        assert response.data[0]['category'] == categories[2].title
        assert response.data[1]['category'] == categories[1].title
        assert response.data[2]['category'] == categories[0].title
        # check only active items were selected
        assert len(response.data[0]['amenities']) == am_cnt1
        assert len(response.data[1]['amenities']) == am_cnt2
        assert len(response.data[2]['amenities']) == am_cnt3
        # check the list contains only the amenities created by the user
        assert response.data[2]['amenities'][0]['title'] == user_amenity.title

    def test_list_no_access(self, db, base_api_client):
        """Test non authorised user can't get list."""
        url = reverse('smp_api:amenity-list')
        response = base_api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_detail_no_access(self, db, authenticated_client):
        """Test users can't get detail of the amenity."""
        amenity = AmenityFactory(is_active=True)
        with pytest.raises(NoReverseMatch):
            reverse('smp_api:amenity-detail', kwargs={'pk': amenity.pk})

    def test_create(self, db, authenticated_client, user, json_data):
        """Test authorised user can create new amenity."""
        url = reverse('smp_api:amenity-list')
        data = {
            'title': json_data(),
            'abbreviation': json_data(),
        }
        response = authenticated_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        amenity = Amenity.objects.get(id=response.data['id'])
        assert amenity.category == self.default_amenity_category
        assert not amenity.is_active
        assert not amenity.is_available_for_house
        assert not amenity.is_available_for_house_space
        assert RequiredVerification.amenities.filter(
            user=user,
            object_id=amenity.id,
        ).count()

    def test_batch_create(self, db, authenticated_client, user, json_data):
        """Test batch creating amenity."""
        url = reverse('smp_api:amenity-batch_create')
        data = [
            {'title': json_data(),
             'abbreviation': json_data()},
            {'title': json_data(),
             'abbreviation': json_data()},
        ]
        response = authenticated_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2
