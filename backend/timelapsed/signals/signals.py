# Directions:

#Locmemcache ase will be used as a caching service. When we make changes in our signals we will write that data into locmemcache. 
#When we are ready to return a response we will build a response from our lomemcache and return it. This allows us to return 
#any and all changes to cards in one response. 

#Need to think a lot about thread safety and especially locks in this function. 


from ..models import Card, Subclass_Relationships, Card_Relationship_Move_Action, Topic, Card_Relationship_Parent_Action, Card_Relationship_Child_Action, Card_Relationship_Delete_Action, Card_Relationship_Subclass_Action
import  timelapsed.services as services
from django.core.cache.backends import locmem
from django.core.signals import request_finished

from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from ..batching.responses import card_response_builder
from searchapp import search



def perform_card_relationship_lookup(relationship):
  for i in relationship:
    parent_actions =Card_Relationship_Parent_Action.objects.filter(Move_ID = i)
    for j in parent_actions:
      try:
        child_action = Card_Relationship_Child_Action(Parent_Action = j)
        #Class that performs this action found in services. 
        services.peform_child_action(child_action)
        child_action.delete()
      finally:
        j.delete()

        #This deletion should also cascade to delete the card action model as well. 



@receiver(pre_save, sender = Card)
def card_save_signal(sender, instance, *args, **kwargs):

  #If Move
  if instance.id != None:

    instance_in_DB = Card.objects.get(id = instance.id)

    if instance_in_DB.Topic != instance.Topic:

      perform_card_relationship_lookup( Card_Relationship_Move_Action.objects.filter(Card_ID = instance, Topic_ID = instance.Topic ))

    else:
      card_response_builder(instance)

    #perform ES call. 

    #NOTE: I am aware this is a non-optimal configuration, a better solution using the ES bulk api needs to be built. This will work for now. 

    # change = search.ElasticSearchCard.get(id = instance.pk)   
    # change.update(Name = instance.Name, Description = instance.Description, Topic = instance.Topic.Name )

  else:

    return



#Delete

@receiver(pre_delete, sender = Card)
def delete_signal(sender, instance, **kwargs):

  #NON-OPTIMAL CONFIGURATION, BUILD ES BATCHING SERVICE 

  # remove = search.ElasticSearchCard.get(id = instance.pk)
  # remove.delete()



  perform_card_relationship_lookup(Card_Relationship_Delete_Action.objects.filter(Card_ID = instance))


#Subclass

@receiver(pre_save, sender = Subclass_Relationships)
def subclass_signal(sender, instance, **kwargs):


  perform_card_relationship_lookup( Card_Relationship_Subclass_Action.objects.filter(Subclass_ID = instance.Subclass, Card_ID = instance.Child_ID))


#Tag
