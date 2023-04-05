from django.test import TestCase, RequestFactory, override_settings
from base.models import ProfileUser, Post, Comment, SecondaryComment, Follower
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import Client
from base.views import PostDetail, PostUpdate, createPost
from base import views
import json
from django.core.files.uploadedfile import SimpleUploadedFile
class TestModelCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_prototypeA = User.objects.create_user(username='A', password='PrototypeA', email='testing@gmail.com')
        self.user_prototypeB = User.objects.create_user(username='B', password='prototypeB', email='testingb@email.com')
        self.user_prototypeD = User.objects.create_user(username='D', password='prototypeD', email='testingd@email.com')
        
        self.client = Client()
        self.client.login(username='A', password='PrototypeA')
        
        self.post_prototypeA = Post.objects.create(username=self.user_prototypeA, description='My post')
        self.post_prototypeB = Post.objects.create(username=self.user_prototypeB, description='My posTB')
        self.post_prototypeC = Post.objects.create(username=self.user_prototypeA, description='My posTC')
        self.post_prototypeD = Post.objects.create(username=self.user_prototypeB, description='My posTD')
        self.post_prototypeE = Post.objects.create(username=self.user_prototypeA, description='My postE')
        
        self.comment_b = Comment.objects.create(post=self.post_prototypeA, username=self.user_prototypeA, comment='My comment')   
        self.follower_prototype_a = Follower.objects.create(follow_user=self.user_prototypeA, user_followed=self.user_prototypeB)
        self.follower_prototype_b = Follower.objects.create(follow_user=self.user_prototypeB, user_followed=self.user_prototypeA)
        self.follower_prototype_c = Follower.objects.create(follow_user=self.user_prototypeD, user_followed=self.user_prototypeA)
        self.follower_prototype_d = Follower.objects.create(follow_user=self.user_prototypeA, user_followed=self.user_prototypeD)

    """
    Testing for models.py
    """          
                
    def test_profile_user_signal(self):
        self.user_prototypeC = User.objects.create_user(username='C', password='PrototypeC')
        self.assertEqual(str(self.user_prototypeC.profile.user.username), 'C')
        self.assertIsInstance(self.user_prototypeC.profile, ProfileUser)
    def test_profile_username(self):
        profile_prototypec = ProfileUser.objects.get(user=self.user_prototypeA)
        self.assertEqual(str(profile_prototypec), 'A')
    #Testing for post
    def test_model_post(self):
        post_a = Post.objects.create(username=self.user_prototypeA, description='Hi')
        post_a.likes.set([self.user_prototypeA, self.user_prototypeB])
        post_a.approve_posts()
        self.assertEquals(post_a.total_likes(), 2)
        self.assertEqual(str(post_a), 'Hi')
    def test_model_comment(self):
        comment_a = Comment.objects.create(post=self.post_prototypeA, username=self.user_prototypeA, comment='My comment')   
        self.assertEquals(comment_a.user_usernames(), 'A')
        self.assertEquals(comment_a.total_likes(), 0)
        self.assertEquals(str(comment_a), 'My comment')
        comment_a.approve()
    def test_secondary_comment(self):
       
        comment = Comment.objects.create(post=self.post_prototypeA, comment='hi', username=self.user_prototypeA)
        secondary = SecondaryComment.objects.create(user=self.user_prototypeB, comment=comment, secondary='Lorem ipsum dolor sit, amet consectetur ajauuauauanaiai a aianiaiaiaiaoaaooq9 aoaja')
        secondaryb = SecondaryComment.objects.create(user=self.user_prototypeA, comment=comment, secondary='Yo')
        self.assertEqual(str(secondary.secondary), 'Lorem ipsum dolor sit, amet consectetur ajauuauauanaiai a aianiaiaiaiaoaaooq9 aoaja')
        self.assertEqual(str(secondaryb.secondary), 'Yo')
        
        
    """
    Testing for views.py
    """  
    def test_views_list(self):
        response = self.client.get(reverse('basic_app:home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/post_list.html')
    def test_views_post_detail(self):
        post_id = self.post_prototypeA.id
        response = self.client.get(reverse('basic_app:post', args=[post_id]))
        self.assertEquals(response.status_code, 200)
    def test_post_upate(self):
        view = PostUpdate()
        post = self.post_prototypeA
        post.description = 'Hii'
        postb = self.post_prototypeB
        postb.description = 'Hii'
        postb.save()
        post.save()
        responseb = self.client.get(reverse('basic_app:edit', args=[postb.id]))
        response = self.client.get(reverse('basic_app:edit', args=[post.id]))

        self.assertEqual(responseb.status_code, 403)
    def test_post_delete(self):
        urla = reverse('basic_app:delete', args=[self.post_prototypeA.id])
        urlb = reverse('basic_app:delete', args=[self.post_prototypeB.id])
        self.client.post(urla)
        self.client.post(urlb)
        response = self.client.get(urla)
        responseB = self.client.get(urlb)
        # Check the status of the response has been deleted i.e 404 not found 
        self.assertEqual(response.status_code, 404)
        # Check if it has been deleted
        self.assertFalse(Post.objects.filter(id=self.post_prototypeA.id).exists())
        # -----------Check if another user is trying to delete a post--------------
        self.assertEqual(responseB.status_code, 403) 
        
    def test_delete_comment(self):
        post = self.post_prototypeC
        postb = self.post_prototypeD
        comment = Comment.objects.create(post=post, username=self.user_prototypeA, comment='hii')
        commentb =  Comment.objects.create(post=postb, username=self.user_prototypeB, comment='hi')
        url = reverse('basic_app:deleteComment', kwargs={
            'post': post.id, 'pk': comment.id
        })
        urlb = reverse('basic_app:deleteComment', kwargs={'post': postb.id, 'pk': commentb.id})
        # 302 the request has been taken to a different location 
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(urlb).status_code, 403)
        
        self.client.post(urlb)
        self.client.post(url)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())
    def test_edit_comment_valid_data(self):
        post = self.post_prototypeA
        comment = Comment.objects.create(post=post, username=self.user_prototypeA, comment='hii')
        url = reverse('basic_app:editComment', kwargs={
            'post': post.id, 'pk': comment.id
        })
        
        response = self.client.post(url, {'comment': 'updated'})
        self.assertRedirects(response, reverse('basic_app:post', args=[post.id]))
        comment.refresh_from_db()
        self.assertEqual(comment.comment, 'updated')
        # self.assertTemplateUsed(response, 'base/comment_edit.html')
        
    def test_edit_comment_invalid_user(self):
        post = self.post_prototypeE
        comment = Comment.objects.create(username=self.user_prototypeB, post=post, comment='hi')
        url = reverse('basic_app:editComment', kwargs={'post': post.id, 'pk': comment.id})
        response = self.client.post(url)
        responseb = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEquals(responseb.status_code, 200)

    def test_create_comment(self):
        post = Post.objects.create(username=self.user_prototypeA, description='post')
        url = reverse('basic_app:comment', args=[post.id])

        response = self.client.post(url, ({'comment': 'my new comment'}))
        responseb = self.client.post(url, ({'comment': ''}))

        # IF RESPONSE IS GET THEN
        responsec = self.client.get(url, ({'comment': 'my new comment'}))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('basic_app:post', args=[post.id]))
        self.assertTrue(Comment.objects.filter(comment='my new comment').exists())
        # Check if the comments len is no greater than 0
        self.assertEquals(responseb.status_code, 302)
        self.assertRedirects(responseb, reverse('basic_app:post', args=[post.id]))

        self.assertEqual(responsec.status_code, 302)
        self.assertRedirects(responsec, reverse('basic_app:post', args=[post.id]))
        
    def test_create_post(self):
        url = reverse('basic_app:create')
        resposnse = self.client.post(url, ({'description': 'create post testing'}))
        resposnsec = self.client.post(url, ({'description': ''}))
        resposnseb = self.client.get(url)
        self.assertEqual(resposnseb.status_code, 302)
        self.assertTrue(Post.objects.filter(description='create post testing'))
    
    def test_create_post_image_given_only(self):
        url = reverse('basic_app:create')
        with open('./media/img/pramod-tiwari-2AfDFg8uC40-unsplash_-_Copy_IaxSqLa.jpg', 'rb') as img:
            response = self.client.post(url, {'description': '','profile_image': SimpleUploadedFile('test_image.jpg', img.read())})
        self.assertEqual(response.status_code, 302)
    def test_create_post_with_description_and_image(self):
        with open('./media/img/pramod-tiwari-2AfDFg8uC40-unsplash_-_Copy_IaxSqLa.jpg', 'rb') as image:
            response = self.client.post(reverse('basic_app:create'), {'description': 'test description', 'profile_image': SimpleUploadedFile('test_img.jpg', image.read())})
        self.assertEqual(response.status_code, 302)
    def test_login(self):
        testuser = User.objects.create_user('testuser', password='testpass')
        # Log in the user
        self.client.login(username='testuser', password='testpass')
        url = reverse('basic_app:login')
        # This response is to check if user exists i.e if user == True
        response = self.client.post(url, {'username': "testuser", 'password': 'A'}, follow=True)

        
        
        self.assertTrue(response.context['user'].is_active)
        self.assertTrue(User.objects.filter(username=response.context['user'].username).exists)
        self.assertEqual(int(self.client.session['_auth_user_id']), testuser.id)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        
        
    def test_login_with_next_url(self):
        user = User.objects.create_user(username='testuserb', password='testpassb')        
        # Log in the user
        url = reverse("basic_app:login")
        #where profile is an anonymous user 
        next_url = url + '?next=profile/AnonymousUser/'
        response = self.client.post(next_url, {"username": "testuserb", "password": "testpassb"})
        # where next_url is none
        next_url_none  = url
        responseb = self.client.post(next_url_none, {"username": "testuserb", "password": "testpassb"})
        
        self.assertRedirects(responseb, reverse('basic_app:profile', args=['testuserb']))

    def test_logout_page(self):
        url = reverse('basic_app:logout')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)   
        # self.assertRedirects(response,reverse('basic_app:home'))     
    def test_validate_username(self):
        url = reverse('basic_app:validate_username_json')
        data = {"username": "A"}
        datab = {"username": "{?????{},,,.,..>;"}
        datac = {"username": "Olawale0019"}

        # data test if it the user already exists, datab tests if the username is alpha numeric, datac tests if the username is valid
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        responseb = self.client.post(url, data=json.dumps(datab), content_type='application/json')
        responsec = self.client.post(url, data=json.dumps(datac), content_type='application/json')
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(responseb['Content-Type'], 'application/json')
        self.assertEqual(responseb.status_code, 400)
        
        received_data = {"error": "This user already exists"}
        received_data_b = {"error": "Please ensure that your username contains only alphanumerics"}
        received_data_c = {"status": True}

        
        response_data = json.loads(response.content)
        response_data_b = json.loads(responseb.content)
        response_data_c = json.loads(responsec.content)
        
        
        self.assertJSONEqual(json.dumps(received_data), response_data)
        self.assertJSONEqual(json.dumps(received_data_b), response_data_b)
        self.assertJSONEqual(json.dumps(received_data_c), response_data_c)
        
    def test_validate_email(self):
        url = reverse('basic_app:validateEmail')
        response_data = {"email": "testing@gmail.com"}
        response_data_b = {"email": "kaija"}
        response_data_c = {"email": "thommy12@gmail.com"}
        
        # data test if it the user already exists, datab tests if the username is alpha numeric, datac tests if the username is valid
        response = self.client.post(url, data=json.dumps(response_data), content_type='application/json')
        responseb = self.client.post(url, data=json.dumps(response_data_b), content_type='application/json')
        responsec = self.client.post(url, data=json.dumps(response_data_c), content_type='application/json')
        
        received_data = {'error': 'This email is already in use'}
        received_data_b = {'error': 'Invalid email'}
        received_data_c = {"status": True}
        
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(responseb['Content-Type'], 'application/json')
        self.assertEqual(responsec['Content-Type'], 'application/json')
      

        self.assertEquals(response.status_code, 400)
        self.assertEquals(responseb.status_code, 400)
        self.assertEquals(responsec.status_code, 200)
        
        self.assertJSONEqual(json.dumps(received_data), json.loads(response.content))
        self.assertJSONEqual(json.dumps(received_data_b), json.loads(responseb.content))
        self.assertJSONEqual(json.dumps(received_data_c), json.loads(responsec.content))              
    def test_validate_password(self):
        url = reverse('basic_app:validate_password')
        
        response_data = {"password": ""}
        response_data_b = {"password": "ZAQ1XDSYAHA"}
        response_data_c = {"password": "kaijaahauaay"}
        response_data_d = {"password": "Zxasw3TA8!@#"}

        
        # data test if it the user already exists, datab tests if the username is alpha numeric, datac tests if the username is valid
        response = self.client.post(url, data=json.dumps(response_data), content_type='application/json')
        responseb = self.client.post(url, data=json.dumps(response_data_b), content_type='application/json')
        responsec = self.client.post(url, data=json.dumps(response_data_c), content_type='application/json')
        responsed = self.client.post(url, data=json.dumps(response_data_d), content_type='application/json')
        
        received_data = {"error": "Please ensure that your password has a minimum length of 7"}
        received_data_b = {"error": "Please ensure that your password contains lowecase letters for security reason"}
        received_data_c = {"error": "Please ensure that your password contains uppercase letters for security reason"}
        received_data_d = {"status": True}
        
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(responseb['Content-Type'], 'application/json')
        self.assertEqual(responsec['Content-Type'], 'application/json')

        self.assertEqual(responseb.status_code, 400)
        
        self.assertJSONEqual(json.dumps(received_data), json.loads(response.content))
        self.assertJSONEqual(json.dumps(received_data_b), json.loads(responseb.content))
        self.assertJSONEqual(json.dumps(received_data_c), json.loads(responsec.content))          
        self.assertJSONEqual(json.dumps(received_data_d), json.loads(responsed.content))          
    def test_confirm_password(self):
        url = reverse('basic_app:validate_confirmPaswoword')
        response_data = {"password": "adsa", "confirmPassword": "adsa"}
        response_data_b = {"password": "ZAQ1XDSYAHA", "confirmPassword": "ZAQ1XDSYAHA"}
        response_data_c = {"password": "kaijaahauaay", "confirmPassword": "kaijaahauaay"}
        response_data_d = {"password": "Zxasmak!@#", "confirmPassword": "zcksTA8ajaja!@#"}
        response_data_e = {"password": "ZxcbagUhajja", "confirmPassword": "ZxcbagUhajja"}


        
        response = self.client.post(url, data=json.dumps(response_data), content_type='application/json')
        responseb = self.client.post(url, data=json.dumps(response_data_b), content_type='application/json')
        responsec = self.client.post(url, data=json.dumps(response_data_c), content_type='application/json')
        responsed = self.client.post(url, data=json.dumps(response_data_d), content_type='application/json')
        responsee = self.client.post(url, data=json.dumps(response_data_e), content_type='application/json')
        
        received_data = {"error": "Please ensure that your password has a minimum length of 7"}
        received_data_b = {"error": "Please ensure that your password contains lowercase letters for security reason"}
        received_data_c = {"error": 'Please ensure that your password contains uppercase letters for security reason'}
        received_data_d = {"error": "Ensure that both passwords are the same"}

        received_data_e = {"status": True}
        
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(responseb['Content-Type'], 'application/json')
        self.assertEqual(responsec['Content-Type'], 'application/json')
        self.assertEqual(responsed['Content-Type'], 'application/json')
        self.assertEqual(responsee['Content-Type'], 'application/json')
        
        self.assertEqual(responseb.status_code, 400)


        self.assertJSONEqual(json.dumps(received_data), json.loads(response.content))
        self.assertJSONEqual(json.dumps(received_data_b), json.loads(responseb.content))
        self.assertJSONEqual(json.dumps(received_data_c), json.loads(responsec.content))          
        self.assertJSONEqual(json.dumps(received_data_d), json.loads(responsed.content))           
        self.assertJSONEqual(json.dumps(received_data_e), json.loads(responsee.content))
                   
    def test_registeration(self):
        url = reverse('basic_app:register')
        # response data a is to check if username is not alphanumeric
        response_data_a = {"firstname": "tommy", "lastname": "dave", "username": "/']\]a", "confirm_password": "Zxsr8jaoIaki9jai&^!", "password": "Zxsr8jaoIaki9jai&^!", "email": "tomyafe1@gmail.com"}
        # response data b is to check if the password does not contains lowercase password   
        response_data_b = {"firstname": "larry", "lastname": "dave", "username": "larry091", "confirm_password": "ZZXVBZUZIA9WJWJ", "password": "ZZXVBZUZIA9WJWJ", "email": "larry1@gmail.com"}
        # response data c is to check if the password does not contains uppercase password
        response_data_c = {"firstname": "barry", "lastname": "allen", "username": "barryburry", "confirm_password": "zxcvbmzzkzmz", "password": "zxcvbmzzkzmz", "email": "burry@gmail.com"}
        # response data d is to check if the email is not valid
        response_data_d = {"firstname": "riley", "lastname": "dave", "username": "Cagaya", "confirm_password": "Zxsr8jaoIaki9jai&^!", "password": "Zxsr8jaoIaki9jai&^!", "email": "tomyA"}
        # response data e is to check if the user already exists
        response_data_e = {"firstname": "riley", "lastname": "dave", "username": "A", "confirm_password": "Zxsr8jaoIaki9jai&^!", "password": "Zxsr8jaoIaki9jai&^!", "email": "atype@gmail.com"}
        # response data f is to check if the email already exists
        response_data_f = {"firstname": "riley", "lastname": "dave", "username": "Abc", "confirm_password": "Zxsr8jaoIaki9jai&^!", "password": "Zxsr8jaoIaki9jai&^!", "email": "testing@gmail.com"}

        # response data g is to check if the length of password is greater than 7
        response_data_g = {"firstname": "dally", "lastname": "wary", "username": "daer091", "confirm_password": "zxCvbnzmlkajUuha&^%", "password": "zxCvbnzmlkajUuha&^%", "email": "tomyAfe1@gmail.com"}
        # response data h is to check if the length of password is greater than 7 and also password is not equal to confirm password
        response_data_h = {"firstname": 'Ahmad', "lastname": "Kassim", "username": "ahmad12", "confirm_password": "zxajaiiajacvbnNmmkzkaao", "password": "zxcvbnNmmkzkaao","email":"ahmad12@gmail.com"}
        # response data i is to check if the length of password is greater than 7 and also password is equal to confirm password
        
        response_data_i = {"firstname": "dally", "lastname": "wary", "username": "joebi091", "confirm_password": "MKiuytayajnahs8", "password": "MKiuytayajnahs8", "email": "to1@gmail.com"}
        # response data j is to check if the length of password is less than 7 
        
        response_data_j = {"firstname": "tomiwa", "lastname": "adenuya", "username": "A", "confirm_password": "t", "password": "", "email": "tomiwa"}
        
        # response data f is to check if the form is valid
        response_data_k = {"firstname": "darry", "lastname": "wary", "username": "darry091", "confirm_password": "zxCvbnzmlkajUuha!@", "password": "zxCvbnzmlkajUuha!@", "email": "tomyAfe1@gmail.com"}        
        #response data m is for the inverse of all of the if statements i.e if the username is alphanumeric, password contains lower and upper case, email is valid, email does not exist, username does not exist and also password is less than 7
        response_data_m = {"firstname": "tommy", "lastname": "tommy", "username": "Zxuyg", "confirm_password": "Za", "password": "Za", "email": "yu@gmail.com"}        
        
        response = self.client.post(url, data=response_data_a) 
        responseb = self.client.post(url, data=response_data_b) 
        responsec = self.client.post(url, data=response_data_c) 
        responsed = self.client.post(url, data=response_data_d) 
        responsee = self.client.post(url, data=response_data_e) 
        responsef = self.client.post(url, data=response_data_f) 
        responseg = self.client.post(url, data=response_data_g) 
        responseh = self.client.post(url, data=response_data_h) 
        responsei = self.client.post(url, data=response_data_i) 
        responsej = self.client.post(url, data=response_data_j) 
        responsek = self.client.post(url, data=response_data_k) 
        responsem = self.client.post(url, data=response_data_m) 
        
        
        
        
        
        
        self.assertEquals(self.client.get(url).status_code, 200)

        self.assertRedirects(response, reverse("basic_app:register"))
        self.assertRedirects(responseb, reverse("basic_app:register"))
        self.assertRedirects(responsec, reverse("basic_app:register"))
        self.assertRedirects(responsed, reverse("basic_app:register"))
        self.assertRedirects(responsee, reverse("basic_app:register"))
        self.assertRedirects(responsef, reverse("basic_app:register"))
        
        self.assertRedirects(responseh, reverse("basic_app:register"))
        self.assertRedirects(responseh, reverse("basic_app:register"))
        self.assertRedirects(responsej, reverse("basic_app:register"))
        self.assertRedirects(responsek, reverse("basic_app:register"))
        self.assertRedirects(responsem, reverse("basic_app:register"))

        
        
        self.assertRedirects(responseg, reverse("basic_app:login"))
        self.assertRedirects(responsei, reverse("basic_app:login"))
    def test_views_profile(self):
        url = reverse('basic_app:profile', args=[self.user_prototypeD.username])

# coverage run manage.py test
# self.assertTrue(Post.objects.filter(username=self.user_prototypeA, pic='img/test_img_RWvxy5J.jpg').exists())
# class TestChatCase(TestCase):
#     pass