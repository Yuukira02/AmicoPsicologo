from django.db import IntegrityError
from django.test import TestCase

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from unittest.mock import patch

from django.urls import reverse
from users.models import PsychologistProfile, Rating, save_psycho_profile, UserProfile

from django.test.client import Client

class TestFunInModels_save_psycho_profile_receiver(TestCase):

    def setUp(self):
        self.psycho = User.objects.create_user(username='test_psycho', password='testpassword12')
        self.client1 = User.objects.create_user(username='test_client1', password='testclientpw1')
        self.client2 = User.objects.create_user(username='test_client2', password='testclientpw2')
        
        self.psycho_profile = PsychologistProfile.objects.create(user=self.psycho)
        self.client1_profile = UserProfile.objects.create(user=self.client1)
        self.client2_profile = UserProfile.objects.create(user=self.client2)

    # che il metodo sia invocabile
    def test_method_is_callable(self):
        self.assertTrue(callable(save_psycho_profile))

    # ROBUSTEZZA
    """input non validi: Instance == not PsychologicalProfile e Instance == None"""
    def test_not_valid_instance_created(self):
        with self.assertRaises(AttributeError):
            save_psycho_profile(sender=PsychologistProfile, instance=self.psycho_profile)

    def test_not_an_instance(self):
        with self.assertRaises(AttributeError):
            save_psycho_profile(sender=Rating, instance=None)

    # COERENZA FUNZIONALE: 
    """controllo che la mia istanza di Psycho sia cambiata 
    come mi aspetto dopo aver effettuato i cambiamenti"""    
    def test_average_as_expected(self):
        rating1 = Rating.objects.create(psycho_to=self.psycho_profile, rating=4, user_from=self.client1_profile)
        rating2 = Rating.objects.create(psycho_to=self.psycho_profile, rating=2, user_from=self.client2_profile)
        rating1.save()
        rating2.save()

        expected_average = (4+2)/2
        self.assertEqual(self.psycho_profile.average_rating, expected_average)
    
class TestView_create_or_update_rating(TestCase):
    def setUp(self):
        self.client = Client()

        self.psycho = User.objects.create(username='test_psycho', password='testpw123')
        self.psycho_profile = PsychologistProfile.objects.create(user=self.psycho)

        self.user = User.objects.create(username='test_user', password='testuserpw12')
        self.user_profile = UserProfile.objects.create(user=self.user)

        self.client.force_login(self.user)

    #CONSISTENZA ARCHITETTURALE:
    def test_context_ratings_is_a_rating(self):
        qs = Rating.objects.all()
        response = self.client.get(reverse('users:myratings'))
        self.assertQuerySetEqual(response.context["ratings"], qs)

    # COERENZA FUNZIONALE
    """Quando non ci sono rating, lo psicologo non deve avere un rating medio. """
    def test_view_psycho_public_profile_if_no_rating_then_None(self):
        response = self.client.get(reverse('users:public_profile', args=(self.psycho_profile.pk,)))
        self.assertContains(response, "None")

    """Quando inserisco un rating, la pagina lo contiene."""
    def test_view_create_object_gets_200_status_code(self):
        rating = Rating.objects.create(user_from=self.user_profile, 
                                       psycho_to=self.psycho_profile, 
                                       rating = 5, 
                                       comment= "Ottimo", 
                                       )
        response = self.client.get(reverse('users:public_profile', args=(self.psycho_profile.pk,)))
        self.assertEqual(response.status_code, 200)

        # Verifica che il rating sia stato effettivamente salvato
        rating = Rating.objects.filter(user_from=self.user_profile, psycho_to=self.psycho_profile).first()
        self.assertIsNotNone(rating)


    """Quando creo un rating, viene modificato con successo""" 
    def test_view_update_rating_and_post(self):
        response = self.client.post(reverse('users:create_or_update_rating', args=(self.psycho_profile.pk,)), 
                                   {"rating":5, 
                                    "comment":"Ottimo"
                                    }, 
                                    follow=False)
        print("RESPONSE:"+str(response))
        # print("REDIRECT-CHAIN:"+str(response.redirect_chain))
        self.assertRedirects(response, reverse('users:public_profile', args=(self.psycho_profile.pk,)))

        response = self.client.get(reverse('users:public_profile', args=(self.psycho_profile.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ottimo")


    # # ROBUSTEZZA
    # """Invio dati sbagliati: rating -1"""
    # def test_not_a_valid_rating_upload_with_negative_value(self):
    #     with self.assertRaises(IntegrityError):
    #         Rating.objects.create(user_from=self.user_profile, 
    #                                 psycho_to=self.psycho_profile, 
    #                                 rating = None, 
    #                                 comment= "banale", 
    #                                 )

        # self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        # self.assertContains(response, "Please fill out this field.")
        

    # """Invio dati sbagliati: rating None"""
    # def test_not_a_valid_rating_upload_with_none_value(self):
    #     with self.assertRaises(TypeError):
    #         self.client.post(reverse('users:create_or_update_rating', args=(self.psycho_profile.pk, )), 
    #                                     {"rating":None, 
    #                                     "comment":"Bravo"
    #                                     }, 
    #                                     follow=True)
    #     response = self.client.get(reverse('users:create_or_update_rating', args=(self.psycho_profile.pk, )))
    #     self.assertEqual(response.status_code, 302)

        
    # """Invio dati sbagliati: rating 7"""
    # def test_not_a_valid_rating_upload_with_out_of_range_value(self):
    #     response = self.client.post(reverse('users:create_or_update_rating', args=(self.psycho_profile.pk,)), 
    #                                {"rating":7, 
    #                                 "comment":"Il migliore"
    #                                 }, 
    #                                 follow=True)
    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
    #     self.assertContains(response, "Please fill out this field.")

    # """Nessun commento"""
    # def test_upload_rating_without_a_comment_gets_error(self):
    #     response = self.client.post(reverse('users:create_or_update_rating', args=(self.psycho_profile.pk,)), 
    #                                {"rating":5, 
    #                                 "rating":""
    #                                 }, 
    #                                 follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
    #     self.assertContains(response, "Please fill out this field.")