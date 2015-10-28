import csv
import inspect
import pickle
import operation as op_lib
import colorama
from colorama import Fore, Back, Style
import readline
import complete

colorama.init()
#print(Fore.RED + text)

LIST_CVS= 'list_cvs'
LIST_PIC= 'list_pic'
ADD = 'add'
readline.parse_and_bind('tab: complete')

"""
                helps= {'s   ': 'to save','a   ': 'to add new operations from csv file',
                        'e   ': 'to edit database', 'l   ':'to list database content',
                        'odb ':'open database file', 'ocvs': 'open csv file' ,
                        'f   ': 'financial review'} 
"""

class UserInterrupt(BaseException):
    """Exception raised for q or Q keyboard enter

    Attributes
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message


class Application():
    
    def __init__(self,args): 
        self.cmd = ""
        self.input_file =None
        self.output_file = None
        self.database_file=None
        self.categories=list()
        self.persons=list()
        self.operations=dict()
        self.db_changed = False
     
        if type(args.cmd) == str: self.cmd = args.cmd
        if type(args.input) == str: self.input_file = args.input
        if type(args.output) == str: self.output_file = args.output
        if type(args.database) == str: self.database_file = args.database
     
        #self.entries=list()
        if self.database_file != None:
            self.load() #load database values from file
    def load(self):
      """
      set Application members
      """
      #try:
      infile=open(self.database_file, "rb")
      loaded = pickle.load(infile)
        
        
      """
      old_operations=loaded['database']
      for key,old_op  in old_operations.items():
          new_op = op_lib.Operation()
          new_op.id = old_op.id
          new_op.category = old_op.category
          new_op.person = old_op.who
          for index in range(7):
              new_op.data[index]=old_op.data[index]
          self.operations[key] = new_op
          att = inspect.getmembers(new_op, lambda a:not(inspect.isroutine(a)))
          print(att)
      """
            
      self.operations=loaded['database']
      self.persons=loaded['whos']
      self.categories=loaded['categories']
      self.db_changed = False
      #except:
      #    print('Could not load database')

    def save(self):
        """
        to_save={'database':self.operations,'categories':self.operations,'whos':self.operations,'id':self.operations}
        """
        try:
            if self.output_file == None: self.output_file = 'budget.pic'
            filename= input("Filename ?[" + self.output_file+ "]>")   
            if filename=='': # si aucune entree prendre celle par defaut
                filename = self.output_file
            outfile=open( filename, "wb" )
            objects={'database':self.operations,'categories':self.categories,'whos':self.persons}
            att = inspect.getmembers(self.operations[0], lambda a:not(inspect.isroutine(a)))
            print(att)


                  
            pickle.dump(objects, outfile)
            outfile.close
            self.db_changed = False
            print('File saved.')
        except:
            print('Error, file not saved')
   
   
    def run(self):
        if self.cmd == LIST_PIC:
            self.list_pic()
        elif self.cmd == ADD:
            self.addFileContent()
        self.menu()
      
    def ask(self,question="?[q]:",default=None,helps=None,new_enable = False):
        """
        Parameters
        **********
        question: str. Question for user
        helps: dictionary containing commands. If not None only commands from help are accepted( plus quit and help)
        new_enable: If True new command is available to add entry to helps list
        
        Return
        ******
        int: User choise 
        raise UserInterrupt: if user choise 'q' or 'Q'
        """
        autowords = list()
        if helps!= None:
            autowords=[word.strip() for word in list(helps)]
        autowords.append('quit')
        autowords.append('help')
        if new_enable == True : autowords.append('new')
        readline.set_completer(complete.SimpleCompleter(autowords).complete)
                
        if default != None:
            question = question + " default["+str(default)+"]: "
        while True: 
            reponse = input(question)
            if reponse == '': 
                if default != None: return default
            elif reponse == 'help':
                """
                if reponses!=None:
                    print(reponses)
                    print("{} : {}".format('new   ', 'new entry'))
                """
                if helps!=None:
                    for key,value in sorted(helps.items()):
                        print("{} : {}".format(key,value ))
                        
                print("{} : {}".format('quit   ', 'return to menu'))
            elif reponse == 'q' or reponse == 'Q' or reponse == 'quit':
                raise UserInterrupt("user want tot quit.")
            
            elif reponse == 'new':
                new_value = input('new value ? >')
                helps.append(new_value)
                self.db_changed = True
                autowords.append(new_value)
                readline.set_completer(complete.SimpleCompleter(autowords).complete)
                continue
            
            #reponse is not empty and not h and not q not new
            if helps == None:
                return reponse
            else: # Help exist
                for key in helps:
                    if key.strip() == reponse.strip():
                        return reponse
                print("not a valid command")
                
                
            
    def ask_int(self,question="?[quit]:", default = None,helps=None):
        return int(self.ask(question,reponses,default,helps))
    
    
    
    def menu(self):
        try:
            while True:
                helps= {'save': 'to save','add ': 'to add new operations from csv file',
                        'edit': 'to edit database', 'list':'to list database content',
                        'open_db ':'open database file', 'open_csv': 'open csv file' ,
                        'financial   ': 'financial review'} 

                cmd=self.ask('budget> ',helps=helps)   
                if cmd == 'quit':
                    break
                elif cmd == 'edit':
                    self.edit()
                elif cmd == 'list':
                    self.list_pic()
                elif cmd == 'add':
                    self.addFileContent()
                elif cmd == 'save':
                    self.save()
                elif cmd == 'open_db':
                    self.open_database_file()
                elif cmd == 'open_csv':
                    self.open_csv_file()
                elif cmd == 'financial':
                    self.financial()
                else: print(cmd, ": command not found")
        except UserInterrupt:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            if  self.db_changed == True:
                while True:
                    reponse = input("Save ? [Yes/no] >")
                    if reponse == '' or reponse == "Y" or reponse =="y" or reponse == "yes" or reponse == "YES":
                        self.save()
                        break
                    elif reponse == 'n' or  reponse == 'N' or  reponse == 'No' or  reponse == 'no':
                        break
       
       
    def financial(self):
        filters=dict()
        try:
            while True:
                try:
                    helps={'pie': 'draw pie', 'balance': 'get balance for current filters', "filters": 'add/suppress filters'} 
                    cmd=self.ask('financial review > ', helps=helps)   
                    if cmd == 'balance':
                        print('account balance : ')
                        solde = 0.
                        for op in self.operations.values():
                            filtered = False
                            for item, value in filters.items():
                                if item == op_lib.data_label[op_lib.category]:
                                    if op.category != value:
                                        filtered = True
                                elif item == op_lib.data_label[op_lib.person]:
                                    if op.person != value:
                                        filtered = True
                                elif item == op_lib.data_label[op_lib.montant]:
                                    montant = float(op.data[op_lib.montant].replace(',', '.'))
                                    signe = value.split()[0].strip()
                                    value =float(value.split()[1].strip())
                                    if signe == ">" :
                                        if montant < value:
                                            filtered = True
                                    elif signe == "<" :
                                        if montant > value:
                                            filtered = True
                                    elif signe == "=":
                                        if montant != value:
                                            filtered = True
                                        
                                elif op.data[op_lib.get_item_id(item)] != value:
                                    filtered = True
                            if filtered == False :
                                print (op)
                                solde+=float(op.data[op_lib.montant].replace(',','.'))
                        if solde >= 0.:
                            print(Back.GREEN)
                        else: print(Back.RED)
                        print('{} : {:,.2f} Eur'.format('Balance   ', solde))
                        print(Style.RESET_ALL)
                    if cmd == 'pie':
                        reponses=('category', 'person')
                        cmd = self.ask("financial pie > ", helps=reponses)
                        by_item={}
                        for op in self.operations.values():
                            montant = float(op.data[op_lib.montant].strip().replace(',','.'))
                            cat = op.category
                            person = op.person
                            if cmd == 'category':
                                if cat in by_item: by_item[cat]+=montant
                                else: by_item[cat]=0.
                            elif cmd == 'person':
                                if person in by_item: by_item[person]+=montant
                                else: by_item[person]=0.
                                
                        
                        total = sum(by_item.values())
                        by_item = { k : v/total*100 for k,v in by_item.items() if v < 0. }
    
                        values = list(by_item.values())
                        labels = list(by_item.keys())
                        
                        import matplotlib.pyplot as plt
                        plt.pie(values, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
                        # Set aspect ratio to be equal so that pie is drawn as a circle.
                        plt.axis('equal')
                        plt.show()
                        
                    elif cmd == 'filters':
                        while True:
                            try: # 
                                helps={'list': 'list active filters', 'add': 'add filter', "suppress": 'suppress filter'} 
                                cmd=self.ask('financial filters > ', helps=helps)   
                                if cmd == "add":
                                    reponses=list(op_lib.data_label.values())
                                    item = self.ask("Add filter > ", helps=reponses)
                                    if item == op_lib.data_label[op_lib.person]:
                                        helps = self.persons
                                    elif item == op_lib.data_label[op_lib.category]:
                                        helps = self.categories
                                    else:
                                        helps=None
                                    new_value = self.ask("new filter value ? >",helps=helps)
                                    filters[item]=new_value
                                elif cmd == 'suppress':
                                    reponses=dict()
                                    for intem,value in list(filters.items()):
                                        reponses[intem] =  value
                                    if len(reponses)>0:
                                        item = self.ask("Enter item  to suppress > ",  helps=reponses)
                                        try:
                                            del filters[item]
                                            print(item, 'suppressed')
                                        except: print("Could not suppress this filter")
                                    else: print('no acvite filter')
                                    
                                elif cmd == 'list':
                                    print('activate filters list:')
                                    print('----------------------')
                                    for item,value in filters.items():
                                        print('{} {}'.format(item,value))
                                    
                            except UserInterrupt:
                                break
                except UserInterrupt:
                    break
        except KeyboardInterrupt:
            pass
                
                
                                   
   

    def edit(self): 
        op_id=None
        while True:
            try:
                helps={'categories':'manage categories', 'persons':'manage persons', 'operations': 'manage operations'} 
                item = self.ask("edit > ",helps=helps)
                #categories
                if item == 'categories' or item == 'c': 
                    while True:
                        try: 
                            reponses = [ 'list', 'add', 'suppress']
                            cmd = self.ask('edit categories >', helps=reponses)
                            if cmd == 'add':
                                new_value = self.ask('new value ? >')
                                self.categories.append(new_value)
                            elif cmd == 'suppress':
                                cat = self.ask('category to supress ? >',helps=self.categories)
                                self.categories.remove(cat)
                            elif cmd == 'list':
                                print(self.categories)
                            self.db_changed = True
                        except UserInterrupt:
                            break
                    
                #whos
                elif item == 'persons' or item == 'p':
                    while True:
                        try: 
                            reponses = [ 'list', 'add', 'suppress']
                            cmd = self.ask('edit persons >', helps=reponses)
                            if cmd == 'add':
                                new_value = self.ask('new value ? >')
                                self.persons.append(new_value)
                            elif cmd == 'suppress':
                                who = self.ask('person to supress ? >',helps=self.persons)
                                self.persons.remove(who)
                            elif cmd == 'list':
                                print(self.persons)
                            self.db_changed = True
                        except UserInterrupt:
                            break
                        
                        
                        
                
                #operations
                elif item == 'operations' or item == 'o':
                    # let user choose an operation
                    while True:
                        try:
                            id_str = ''
                            choix = { 'edit': 'edit current operation', 'suppress': 'suppress current operation', 'select': 'select current operation', 'list': 'list operations'}
                            if op_id != None:
                                cmd=self.ask('edit operation '+ str(op_id) + '>  ',helps=choix)
                            else:
                                cmd=self.ask('edit operations >',helps=choix)
                            if cmd == 'edit':
                                if ( op_id != None):
                                    op.category=self.ask('    category?: ',default=op.category,helps=cats)
                                    op.person=self.ask('    person?: ',default=op.person,helps=self.persons)
                                    op.data[op_lib.libelle]=self.ask('    libelle ? :'+ op.data[op_lib.libelle],default=op.data[op_lib.libelle])
                                    print(Back.GREEN)
                                    print(op)
                                    print(Style.RESET_ALL)
                                    self.db_changed = True
                                else:
                                    print('select an operation first.')
                            elif cmd == 'suppress':
                                if ( op_id != None):
                                    sure = input("Sure ? [Yes/no]:")
                                    if sure == '' or sure == 'y' or sure == 'Y' or sure == 'yes' or sure == 'YES' or sure == 'Yes':
                                        del self.operations[op_id]
                                        print("done.")
                                        self.db_changed = True
                                        od = None
                                        op_id=None
                                        self.db_changed = True
                                else:
                                    print('select an operation first.')
                                pass
                            elif cmd == 'select':
                                print("operations listing:",self.operations)
                                op_id = self.ask_int('operatoperations id ?:')
                                op = self.operations[op_id]
                                # user can set new value or let existing one
                                print(Back.BLACK)
                                print("current operation for edition :\n", op)
                                print(Style.RESET_ALL)
                            elif cmd == 'list':
                                print(self.operations)
                                
                            
                        except KeyError:
                            print("none existing operation")
                            od = None
                            op_id=None
        
            except UserInterrupt:
                break
            except KeyboardInterrupt:
                pass
                    
    def addFileContent(self):
    #CATEGORIE
        if self.input_file == None:
            self.input_file = self.ask("input file? :",default='data.csv')
        try :
            with open(self.input_file,encoding='mac_roman', newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
                next(spamreader)# rows title
                try:
                    for line in spamreader:
                        #fill from file  
                        new_operation = op_lib.Operation(line)
                        exist=False
                        for operation in self.operations.values():
                            if operation == new_operation:
                                exist=True
                                # Add existing operation to list that will be save
                                continue
                        if exist: continue
                        new_operation.id = self.get_next_id()
                        print(Back.BLACK)
                        print(new_operation)
                        print(Style.RESET_ALL)
                        new_operation.category=self.ask('category > ',helps=self.categories,new_enable=True)
                        new_operation.person=self.ask('person ? > ',helps=self.persons,new_enable=True)
                        reponse=input(new_operation.data[op_lib.libelle]+ " :" )
                        if reponse != '' :
                            new_operation.data[op_lib.libelle]=reponse
                        self.operations[new_operation.id]=new_operation
                        print(Back.GREEN)
                        print(new_operation)
                        print(Style.RESET_ALL)
                        self.db_changed = True
                except UserInterrupt:
                    pass
                except KeyboardInterrupt:
                    pass
                finally:
                    csvfile.close() 
        except FileNotFoundError:
            print('Could not open', self.input_file)
           
 
    def list_pic(self):
        print('operations',self.operations)
        print('person',self.persons)
        print('categories',self.categories)


    def get_next_id(self):
        
        return max(self.operations.keys())+1
    
    
    def open_database_file(self):
        self.database_file = self.ask("database file name ?: ")
        self.load()

    
    def open_csv_file(self):
        self.input_file = self.ask("csv input filename ?: ")
        
