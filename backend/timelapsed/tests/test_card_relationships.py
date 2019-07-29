from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from ..models import Users, Topic, Date_Range, Card, Subclass, Topic_Relationships,  Subclass_Relationships, Card_Relationship_Parent_Action, Card_Relationship_Child_Action, Card_Relationship_Move_Action, Card_Relationship_In_Same_Action, Card_Relationship_Delete_Action, Card_Relationship_Subclass_Action

from django.test import TestCase

import json

from django.core.exceptions import ObjectDoesNotExist

import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError


## Use decode_response do get object payload ##


def decode_response(res):
  d = res.content.decode()
  return json.loads(d)



class TestCardRelationshipResponses(APITestCase):
  parent_id = 0
  first_child_id = 0
  first_topic_id = 0  
  second_topic_id = 1
  first_subclass_id = 0

  def setUp(self):
    #Runs before every test

    ###USE THE FOLLOWING BOILERPLATE BEFORE EVERY REQUEST###
    user = User.objects.create_user('test@test.com', 'test@test.com')
    self.client.force_authenticate(user)
    parent_card = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')    
    self.parent_id =  decode_response(parent_card)['Data']['id'] 
    first_child_card = self.client.post('/api/card/', {'Data': {'Name': 'Second', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')    
    self.first_child_id =  decode_response(first_child_card)['Data']['id']    
    ######################################################


  @classmethod
  def setUpTestData(cls):
    Users.objects.create(Email = 'test@test.com')
    set_up_topic = Topic.objects.create(Name = 'UseForTesting', Position = 1, Email = Users.objects.get(Email = 'test@test.com') )
    cls.topic_id = set_up_topic.id
    set_up_second_topic = Topic.objects.create(Name = 'UseForTesting2', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )
    cls.second_topic_id = set_up_second_topic.id
    subclass_head = Card.objects.create(Name = 'Subclass_Head', Description = 'Head For Subclass', Position = 1, Email = Users.objects.get(Email = 'test@test.com'), Topic = set_up_topic)
    first_subclass = Subclass.objects.create(Email = Users.objects.get(Email = 'test@test.com'), Head = subclass_head)
    cls.first_subclass_id = first_subclass.id

  def test_if_rejects_without_parent(self):
    
    response = self.client.post('/api/card_relationship/', {'Child_Action': {'Delete': {'Card_ID': self.parent_id}}}, format = 'json')

    self.assertEqual(response.status_code, 400)

  
  def test_if_rejects_multiple_parent_relationships(self):
    
    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : self.first_child_id, 'Topic_ID' : self.second_topic_id}, 'Delete': {'Card_ID': self.first_child_id} }, 'Child_Action': {'Delete': {'Card_ID': self.parent_id}}}, format = 'json')

    self.assertEqual(response.status_code, 400)

  def test_if_rejects_with_non_same_parent_and_no_child(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : self.first_child_id, 'Topic_ID' : self.second_topic_id}}}, format = 'json'  )

    self.assertEqual(response.status_code, 400)


  def test_if_accepts_moves(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : self.first_child_id, 'Topic_ID' : self.second_topic_id}},'Child_Action': {'Delete': {'Card_ID': self.parent_id}}}, format = 'json'  )

    self.assertEqual(response.status_code, 201)


  def test_if_accepts_valid_parent_same(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Same': {'Card_ID': self.parent_id, 'Child_ID': self.first_child_id}}}, format = 'json')


    self.assertEqual(response.status_code, 201)

  def test_if_accepts_valid_deletes(self):
    
    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Delete': {'Card_ID': self.parent_id}}, 'Child_Action': {'Delete': {'Card_ID': self.first_child_id}} }, format = 'json')


    self.assertEqual(response.status_code, 201)


  def test_if_accepts_valid_subclasses(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Subclass': {'Card_ID': self.first_child_id, 'Subclass_ID': self.first_subclass_id}}, 'Child_Action': {'Subclass': {'Card_ID': self.parent_id, 'Subclass_ID': self.first_subclass_id}} }, format = 'json')


    self.assertEqual(response.status_code, 201)    


  def test_if_rejects_multiple_child_relationships(self):
    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Subclass': {'Card_ID': self.parent_id, 'Subclass_ID': self.first_subclass_id}}, 'Child_Action': {'Subclass': {'Card_ID': self.first_child_id, 'Subclass_ID': self.first_subclass_id}, 'Delete': {'Card_ID': self.first_child_id } }}, format = 'json')


    self.assertEqual(response.status_code, 400)    


  def test_if_rejects_empty_child_actions(self):
    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Subclass': {'Card_ID': self.parent_id, 'Subclass_ID': self.first_subclass_id}}} , format = 'json')


    self.assertEqual(response.status_code, 400)    

  def test_if_rejects_actions_on_same_card(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Delete': {'Card_ID': self.parent_id}}, 'Child_Action': {'Delete': {'Card_ID': self.parent_id}} }, format = 'json')


    self.assertEqual(response.status_code, 400)    

  def test_if_move_rejects_with_invalid_card_id(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : 8000000000, 'Topic_ID' : self.second_topic_id}},'Child_Action': {'Delete': {'Card_ID': self.parent_id}}}, format = 'json'  )

    self.assertEqual(response.status_code, 400)


  def test_if_move_rejects_with_invalid_topic_id(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : self.first_child_id, 'Topic_ID' : 800000}},'Child_Action': {'Delete': {'Card_ID': self.parent_id}}}, format = 'json'  )

    self.assertEqual(response.status_code, 400)


  def test_if_same_rejects_with_invalid_card_id(self):


    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Same': {'Card_ID': 8000000000, 'Child_ID': self.first_child_id}}}, format = 'json')


    self.assertEqual(response.status_code, 400)

  def test_if_same_rejects_with_invalid_child_id(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Same': {'Card_ID': self.parent_id, 'Child_ID': 8000000000000}}}, format = 'json')


    self.assertEqual(response.status_code, 400)


  def test_if_same_rejects_if_child_and_card_are_same(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Same': {'Card_ID': self.parent_id, 'Child_ID': self.parent_id}}}, format = 'json')


    self.assertEqual(response.status_code, 400)

  def test_if_delete_rejects_with_invalid_card_id(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Delete': {'Card_ID': 8000000000000000}}, 'Child_Action': {'Delete': {'Card_ID': self.first_child_id}} }, format = 'json')


    self.assertEqual(response.status_code, 400)


  def test_if_subclass_rejects_with_invalid_card_id(self):


    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Subclass': {'Card_ID': 800000000000, 'Subclass_ID': self.first_subclass_id}}, 'Child_Action': {'Subclass': {'Card_ID': self.first_child_id, 'Subclass_ID': self.first_subclass_id}} }, format = 'json')


    self.assertEqual(response.status_code, 400)    

  def test_if_subclass_rejects_with_invalid_subclass_id(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Subclass': {'Card_ID': self.parent_id, 'Subclass_ID': 8000000000}}, 'Child_Action': {'Subclass': {'Card_ID': self.first_child_id, 'Subclass_ID': self.first_subclass_id}} }, format = 'json')


    self.assertEqual(response.status_code, 400)    

  def test_if_move_rejects_if_already_in_that_topic(self):
    pass

  #Add tests for deletion



class TestCardRelationshipCreation(APITestCase):
  parent_id = 0
  first_child_id = 0
  first_topic_id = 0  
  second_topic_id = 1
  first_subclass_id = 0

  def setUp(self):
    #Runs before every test

    ###USE THE FOLLOWING BOILERPLATE BEFORE EVERY REQUEST###
    user = User.objects.create_user('test@test.com', 'test@test.com')
    self.client.force_authenticate(user)
    parent_card = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')    
    self.parent_id =  decode_response(parent_card)['Data']['id'] 
    first_child_card = self.client.post('/api/card/', {'Data': {'Name': 'Second', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')    
    self.first_child_id =  decode_response(first_child_card)['Data']['id']    
    ######################################################


  @classmethod
  def setUpTestData(cls):
    Users.objects.create(Email = 'test@test.com')
    set_up_topic = Topic.objects.create(Name = 'UseForTesting', Position = 1, Email = Users.objects.get(Email = 'test@test.com') )
    cls.topic_id = set_up_topic.id
    set_up_second_topic = Topic.objects.create(Name = 'UseForTesting2', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )
    cls.second_topic_id = set_up_second_topic.id
    subclass_head = Card.objects.create(Name = 'Subclass_Head', Description = 'Head For Subclass', Position = 1, Email = Users.objects.get(Email = 'test@test.com'), Topic = set_up_topic)
    first_subclass = Subclass.objects.create(Email = Users.objects.get(Email = 'test@test.com'), Head = subclass_head)
    cls.first_subclass_id = first_subclass.id

  def test_if_properly_creates_parent_action(self):
    pass
  def test_if_properly_creates_child_action(self):
    pass

  def test_if_properly_creates_move_relationship(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : self.first_child_id, 'Topic_ID' : self.topic_id}},'Child_Action': {'Delete': {'Card_ID': self.parent_id}}}, format = 'json'  )

    parent_relationship_id = decode_response(response)['Parent']['id']

    parent_relationship = Card_Relationship_Parent_Action.objects.get(id = parent_relationship_id)

    move_relationship = parent_relationship.Move_ID

    self.assertEqual(move_relationship.Card_ID.id, self.first_child_id)
    self.assertEqual(move_relationship.Topic_ID.id, self.topic_id)


  def test_if_properly_creates_same_relationship(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Same': {'Card_ID': self.parent_id, 'Child_ID': self.first_child_id}}}, format = 'json')

    parent_relationship_id = decode_response(response)['Parent']['id']

    parent_relationship = Card_Relationship_Parent_Action.objects.get(id = parent_relationship_id)

    same_relationship = parent_relationship.Same_ID

    self.assertEqual(same_relationship.Card_ID.id, self.parent_id)
    self.assertEqual(same_relationship.Child_ID.id, self.first_child_id)


  def test_if_properly_creates_subclass_relationship(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Subclass': {'Card_ID': self.first_child_id, 'Subclass_ID': self.first_subclass_id}}, 'Child_Action': {'Subclass': {'Card_ID': self.parent_id, 'Subclass_ID': self.first_subclass_id}} }, format = 'json')
    
    parent_relationship_id = decode_response(response)['Parent']['id']

    parent_relationship = Card_Relationship_Parent_Action.objects.get(id = parent_relationship_id)

    subclass_relationship = parent_relationship.Subclass_ID

    self.assertEqual(subclass_relationship.Card_ID.id, self.first_child_id)
    self.assertEqual(subclass_relationship.Subclass_ID.id, self.first_subclass_id)

  def test_if_properly_creates_delete_relationship(self):
    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Delete': {'Card_ID': self.parent_id}}, 'Child_Action': {'Delete': {'Card_ID': self.first_child_id}} }, format = 'json')
   
    delete_relationship_id = decode_response(response)['Parent']['id']

    delete_relationship = Card_Relationship_Delete_Action.objects.get(id = delete_relationship_id)

    self.assertEqual(delete_relationship.Card_ID.id, self.parent_id)



class TestCardRelationshipFunctionality(APITestCase):
  parent_id = 0
  first_child_id = 0
  topic_id = 0  
  second_topic_id = 1
  first_subclass_id = 0

  def setUp(self):
    #Runs before every test

    ###USE THE FOLLOWING BOILERPLATE BEFORE EVERY REQUEST###
    user = User.objects.create_user('test@test.com', 'test@test.com')
    self.client.force_authenticate(user)
    parent_card = self.client.post('/api/card/', {'Data': {'Name': 'First', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')    
    self.parent_id =  decode_response(parent_card)['Data']['id'] 
    first_child_card = self.client.post('/api/card/', {'Data': {'Name': 'Second', 'Description': 'Test', 'Topic': self.topic_id}}, format = 'json')    
    self.first_child_id =  decode_response(first_child_card)['Data']['id']    
    ######################################################


  @classmethod
  def setUpTestData(cls):
    Users.objects.create(Email = 'test@test.com')
    set_up_topic = Topic.objects.create(Name = 'UseForTesting', Position = 1, Email = Users.objects.get(Email = 'test@test.com') )
    cls.topic_id = set_up_topic.id
    set_up_second_topic = Topic.objects.create(Name = 'UseForTesting2', Position = 2, Email = Users.objects.get(Email = 'test@test.com') )
    cls.second_topic_id = set_up_second_topic.id
    subclass_head = Card.objects.create(Name = 'Subclass_Head', Description = 'Head For Subclass', Position = 1, Email = Users.objects.get(Email = 'test@test.com'), Topic = set_up_topic)
    first_subclass = Subclass.objects.create(Email = Users.objects.get(Email = 'test@test.com'), Head = subclass_head)
    cls.first_subclass_id = first_subclass.id


  def test_if_properly_moves_child_card(self):
    

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : self.parent_id, 'Topic_ID' : self.second_topic_id}},'Child_Action': {'Move': {'Card_ID': self.first_child_id, 'Topic_ID': self.second_topic_id}}}, format = 'json'  )

    second = self.client.put(f'/api/card/{self.parent_id}/', {'Data': {'Switch_Topic': self.second_topic_id}}, format = 'json' )    

    second_response =  decode_response(second)

    #Check if response is correct. 

    self.assertEqual(second_response['Edit'][f'{self.parent_id}']['Topic'], self.second_topic_id)
    self.assertEqual(second_response['Edit'][f'{self.parent_id}']['Topic'], second_response['Edit'][f'{self.first_child_id}']['Topic'])    


    self.assertEqual(Card.objects.get(id = self.first_child_id).Topic.id, self.second_topic_id)
    self.assertEqual(Card.objects.get(id = self.parent_id).Topic.id, self.second_topic_id)    


  def test_if_same_properly_works_as_parent(self):

    self.client.post('/api/card_relationship/', {'Parent_Action': {'Same': {'Card_ID': self.parent_id, 'Child_ID': self.first_child_id}}}, format = 'json')

    second = self.client.put(f'/api/card/{self.parent_id}/', {'Data': {'Switch_Topic': self.second_topic_id}}, format = 'json' )   
    
    second_response =  decode_response(second)

    #Check if response is correct. 

    self.assertEqual(second_response['Edit'][f'{self.parent_id}']['Topic'], self.second_topic_id)
    self.assertEqual(second_response['Edit'][f'{self.parent_id}']['Topic'], second_response['Edit'][f'{self.first_child_id}']['Topic'])  

    self.assertEqual(Card.objects.get(id = self.first_child_id).Topic.id, self.second_topic_id)

  def test_if_same_properly_works_as_child(self):
    self.client.post('/api/card_relationship/', {'Parent_Action': {'Same': {'Card_ID': self.parent_id, 'Child_ID': self.first_child_id}}}, format = 'json')

    second = self.client.put(f'/api/card/{self.first_child_id}/', {'Data': {'Switch_Topic': self.second_topic_id}}, format = 'json' )   
    
    second_response =  decode_response(second)

    #Check if response is correct. 

    self.assertEqual(second_response['Edit'][f'{self.parent_id}']['Topic'], self.second_topic_id)
    self.assertEqual(second_response['Edit'][f'{self.parent_id}']['Topic'], second_response['Edit'][f'{self.first_child_id}']['Topic'])  


    self.assertEqual(Card.objects.get(id = self.parent_id).Topic.id, self.second_topic_id)

  def test_if_subclass_properly_works(self):

    self.client.post('/api/card_relationship/', {'Parent_Action': {'Subclass': {'Card_ID': self.parent_id, 'Subclass_ID': self.first_subclass_id}}, 'Child_Action': {'Subclass': {'Card_ID': self.first_child_id, 'Subclass_ID': self.first_subclass_id}} }, format = 'json')
    
    response = self.client.put(f'/api/subclass/{self.first_subclass_id}/', {'Add': [self.parent_id]})

    subclass_response = decode_response(response)['Subclass']

    #Test Response

    self.assertTrue(self.parent_id in subclass_response['Add'][f'{self.first_subclass_id}'])
    self.assertTrue(self.first_child_id in subclass_response['Add'][f'{self.first_subclass_id}'])

    self.assertTrue(Subclass_Relationships.objects.filter(Subclass = self.first_subclass_id, Child_ID = self.parent_id).exists())
    self.assertTrue(Subclass_Relationships.objects.filter(Subclass = self.first_subclass_id, Child_ID = self.first_child_id).exists())    


  def test_if_delete_properly_works(self):

    self.client.post('/api/card_relationship/', {'Parent_Action': {'Delete': {'Card_ID': self.parent_id}}, 'Child_Action': {'Delete': {'Card_ID': self.first_child_id}} }, format = 'json')

    response = self.client.delete(f'/api/card/{self.parent_id}/')    

    delete_response = decode_response(response)['Delete']


    self.assertTrue(self.parent_id in delete_response)
    self.assertTrue(self.first_child_id in delete_response)


    with self.assertRaises(ObjectDoesNotExist):
      Card.objects.get(id = self.parent_id)
    with self.assertRaises(ObjectDoesNotExist):
      Card.objects.get(id = self.first_child_id)
  
  def test_if_can_mix_move_and_subclass(self):
   
    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : self.parent_id, 'Topic_ID' : self.second_topic_id}}, 'Child_Action': {'Subclass': {'Card_ID': self.first_child_id, 'Subclass_ID': self.first_subclass_id}} }, format = 'json'  )

    second = self.client.put(f'/api/card/{self.parent_id}/', {'Data': {'Switch_Topic': self.second_topic_id}}, format = 'json' )   

    second_response = decode_response(second)

    #Test responses. 

    self.assertEqual(second_response['Edit'][f'{self.parent_id}']['Topic'], self.second_topic_id)
    self.assertTrue(self.first_child_id in second_response['Subclass']['Add'][f'{self.first_subclass_id}'])


    self.assertEqual(Card.objects.get(id = self.parent_id).Topic.id, self.second_topic_id)  
    self.assertTrue(Subclass_Relationships.objects.filter(Subclass = self.first_subclass_id, Child_ID = self.first_child_id).exists())          


  def test_if_can_mix_subclass_and_move(self):

    self.client.post('/api/card_relationship/', {'Parent_Action':{'Subclass': {'Card_ID': self.parent_id, 'Subclass_ID': self.first_subclass_id}} , 'Child_Action': {'Move': {'Card_ID' : self.first_child_id, 'Topic_ID' : self.second_topic_id}} }, format = 'json'  )

    second = self.client.put(f'/api/subclass/{self.first_subclass_id}/', {'Add': [self.parent_id]})

    second_response = decode_response(second)


    self.assertTrue(self.parent_id in second_response['Subclass']['Add'][f'{self.first_subclass_id}'])


    self.assertTrue(Subclass_Relationships.objects.filter(Subclass = self.first_subclass_id, Child_ID = self.parent_id).exists())
    self.assertEqual(Card.objects.get(id = self.first_child_id).Topic.id, self.second_topic_id)

  def test_if_can_mix_move_and_delete(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Move': {'Card_ID' : self.parent_id, 'Topic_ID' : self.second_topic_id}}, 'Child_Action': {'Delete': {'Card_ID': self.first_child_id}}}, format = 'json'  )

    second = self.client.put(f'/api/card/{self.parent_id}/', {'Data': {'Switch_Topic': self.second_topic_id}}, format = 'json' )   

    second_response = decode_response(second)    


    self.assertEqual(second_response['Edit'][f'{self.parent_id}']['Topic'], self.second_topic_id)
    self.assertTrue(self.first_child_id in second_response['Delete'])


    self.assertEqual(Card.objects.get(id = self.parent_id).Topic.id, self.second_topic_id) 
    with self.assertRaises(ObjectDoesNotExist):
      Card.objects.get(id = self.first_child_id)

  def test_if_can_mix_delete_and_move(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Delete': {'Card_ID': self.parent_id}}, 'Child_Action': {'Move': {'Card_ID' : self.first_child_id, 'Topic_ID' : self.second_topic_id}}}, format = 'json'  )

    second = self.client.delete(f'/api/card/{self.parent_id}/')   

    second_response = decode_response(second)    


    self.assertEqual(second_response['Edit'][f'{self.first_child_id}']['Topic'], self.second_topic_id)
    self.assertTrue(self.parent_id in second_response['Delete'])


    self.assertEqual(Card.objects.get(id = self.first_child_id).Topic.id, self.second_topic_id) 

    with self.assertRaises(ObjectDoesNotExist):
      Card.objects.get(id = self.parent_id)



  def test_if_can_mix_delete_and_subclass(self):

    response = self.client.post('/api/card_relationship/', {'Parent_Action': {'Delete': {'Card_ID': self.parent_id}}, 'Child_Action': {'Subclass': {'Card_ID': self.first_child_id, 'Subclass_ID': self.first_subclass_id}}}, format = 'json'  )

    second = self.client.delete(f'/api/card/{self.parent_id}/')   

    second_response = decode_response(second)    

    self.assertTrue(self.parent_id in second_response['Delete'])
    self.assertTrue(self.first_child_id in second_response['Subclass']['Add'][f'{self.first_subclass_id}'])

    

    self.assertTrue(Subclass_Relationships.objects.filter(Subclass = self.first_subclass_id, Child_ID = self.first_child_id).exists())
    with self.assertRaises(ObjectDoesNotExist):
      Card.objects.get(id = self.parent_id)

  def test_if_can_mix_subclass_and_delete(self):


    self.client.post('/api/card_relationship/', {'Parent_Action':{'Subclass': {'Card_ID': self.parent_id, 'Subclass_ID': self.first_subclass_id}}, 'Child_Action': {'Delete': {'Card_ID': self.first_child_id} }}, format = 'json'  )

    second = self.client.put(f'/api/subclass/{self.first_subclass_id}/', {'Add': [self.parent_id]})  
   
    second_response = decode_response(second)    


    self.assertTrue(self.first_child_id in second_response['Delete'])
    self.assertTrue(self.parent_id in second_response['Subclass']['Add'][f'{self.first_subclass_id}'])

    

    self.assertTrue(Subclass_Relationships.objects.filter(Subclass = self.first_subclass_id, Child_ID = self.parent_id).exists())

    with self.assertRaises(ObjectDoesNotExist):
      Card.objects.get(id = self.first_child_id)

  def test_if_same_is_removed_when_one_card_is_removed(self):
    pass
  def test_if_subclass_is_removed_when_subclass_is_deleted(self):
    pass
  def test_if_move_is_removed_when_topic_is_deleted(self):
    pass

  def test_if_properly_moves_multiple_chained_cards(self):
    pass
  def test_if_deletes_same_if_either_card_is_deleted(self):
    pass

  def test_if_does_not_create_multiples_if_relationship_already_exists(self):
    pass
  def test_if_properly_deletes_out_old_relationships(self):

    pass
  def test_if_does_not_create_multiple_parents_for_same_action(self):
    pass
  
  
