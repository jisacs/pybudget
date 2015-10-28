import sys


compte=0
date_comptabilisation=1
date_operation=2
libelle=3
reference=4
date_valeur=5
montant=6
category=7
person=8


data_label=dict()
data_label[compte]='compte'
data_label[date_comptabilisation]='date_comptabilisation'
data_label[date_operation]='date_operation'
data_label[libelle]='libelle'
data_label[reference]='reference'
data_label[date_valeur]='date_valeur'
data_label[montant]='montant'
data_label[category]='category'
data_label[person]='person'


class Operation():
    
    
  def __init__(self,cvs_row=None):
    """
    Parameter:
    **********
    cvs_row: list
            string return with csv libray:
    """
    self.id = -1
    self.category = str()
    self.person = str()
    self.data=dict()
    
    if cvs_row != None:
        for idx, value in enumerate(cvs_row):
            self.data[idx]=value
    else:
        for index in range(7):
            self.data[index]=''
    
     
  
  def __repr__(self):
    result =  str("\n** Operation:[ "+str(self.id) + "]: " + self.data[libelle] +
              "\n** compte: "+ self.data[compte]+
              "\n** date operation: " + self.data[date_operation]+ 
              "\n** reference: " + self.data[reference]+ 
              "\n** date de valeur: " + self.data[date_valeur]+
              "\n** MONTANT: " + self.data[montant]+ 
              "\n** category: "+  self.category +
              "\n** person: " + self.person +"\n")
    return result

  def __eq__(self, other):
      
      result= (isinstance(other, self.__class__)
          and self.data[reference] == other.data[reference]
          and self.data[compte] == other.data[compte]
          and self.data[montant] == other.data[montant]
          )
      return result

  def __ne__(self, other):
        return not self.__eq__(other)


def get_item_id(item):
    if item == data_label[compte]: return compte
    if item == data_label[date_operation] :return date_operation
    if item == data_label[libelle] :return libelle
    if item == data_label[reference]: return reference
    if item == data_label[date_valeur]: return date_valeur
    if item == data_label[montant]: return montant
    if item == data_label[category]: return category
    if item == data_label[person]: return person