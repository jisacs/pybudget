import csv
import numpy as np
import math
import matplotlib.pyplot as plt
import inspect
import pickle
import operation as op_lib
import colorama
from colorama import Fore, Back, Style
import readline
from operator import itemgetter
import complete

colorama.init()
#print(Fore.RED + text)

LIST_CVS= 'list_cvs'
LIST_PIC= 'list_pic'
ADD = 'add'
readline.parse_and_bind('tab: complete')

POSITIVE_FILTER = 'POS'
NEGATIVE_FILTER = 'NEG'

class UserInterrupt(BaseException):
    """Exception raised for quit, q or Q keyboard enter
    Attributes
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message


class Application():
    
    def __init__(self,args): 
        self.cmd = ""
        self.input_file =None
        self.database_file=None
        self.categories=list()
        self.persons=list()
        self.operations=dict()
        self.db_changed = False
        self.filters=dict()
     
        if type(args.cmd) == str: self.cmd = args.cmd
        if type(args.input) == str: self.input_file = args.input
        if type(args.database) == str: self.database_file = args.database
     
        if self.database_file != None:
            self.load() #load database values from file
    def load(self):
      """
      load Application members from self.input_file)
      """
      try:
          infile=open(self.database_file, "rb")
          loaded = pickle.load(infile)
          self.operations=loaded['database']
          self.persons=loaded['whos']
          self.categories=loaded['categories']
          self.db_changed = False
      except:
          print("could not open", self.database_file)

    def save(self):
        """
        Save self.operations, self.categories and self.persons to self.database_file
        """
        try:
            if self.database_file == None: self.database_file = 'budget.pic'
            filename= input("Filename ?[" + self.database_file+ "]>")   
            if filename=='': # si aucune entree prendre celle par defaut
                filename = self.database_file
            outfile=open( filename, "wb" )
            objects={'database':self.operations,'categories':self.categories,'whos':self.persons}
            pickle.dump(objects, outfile)
            outfile.close()
            self.db_changed = False
            print('File saved.')
        except:
            print('Error, file not saved')
   
   
    def run(self):
        """
        Application Run 
        """
        if self.cmd == LIST_PIC:
            self.list_pic()
        elif self.cmd == ADD:
            self.addFileContent()
        self.menu()
      
    def ask(self,question="?[q]:",default=None,helps=None,new_enable = False):
        """
        Wait until  user input is coorect and return it.
        Tab completation is construct on helps list/dict
        Parameters
        **********
        question: str. Question for user
        helps: list/dict, containing commands. If not None only commands from help are accepted( plus quit and help
        default: str, return default is user return ''
        new_enable: If True new command is available to be added to helps list
        
        Returns
        ******
        str: User choice
        raise UserInterrupt: if user choise is quit', 'q' or 'Q'
        """
        # prepare autowords for tab completion
        autowords = list()
        if helps!= None:
            autowords=[word.strip() for word in list(helps)]
        autowords.append('quit')
        autowords.append('help')
        if new_enable == True : autowords.append('new')
        readline.set_completer(complete.SimpleCompleter(autowords).complete)
        
        # set prompt        
        if default != None:
            question = question + " default["+str(default)+"]: "
            
        # Until user enter a valid response    
        while True: 
            reponse = input(question)
            # User enter default ('') ?
            if reponse == '': 
                if default != None: return default
            # USer enter help
            elif reponse == 'help':
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
                # add new value to tab_completion and continue
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
        """
        return int from self.ask()
        """
        return int(self.ask(question,default,helps))
    
    
    
    def menu(self):
        try:
            while True:
                helps= {'filters': 'list/add suppress filters', 'save': 'to save','add ': 'to add new operations from csv file',
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
                elif cmd == 'filters':
                    self.manage_filters()
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
       
       
    def get_filtered_operations(self): 
        """
        return dict containing only filtered operations
        """
        result = dict()
        for op in self.operations.values():
            filtered = False
            for item, value in self.filters.items():
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
                    
            if filtered == False:
                result[op.id]=op
        return result
    
    
    def balance(self):
        """
        Compute and display account balance filtered by self.filters
        """
        debit_solde = 0.
        credit_solde = 0.
        filtered_operations = self.get_filtered_operations()
            
        for op in filtered_operations.values():
            value = float(op.data[op_lib.montant].replace(',','.'))
            if value >0.:
                print(Back.GREEN)
                credit_solde+=float(op.data[op_lib.montant].replace(',','.'))
                print (op)
                print(Style.RESET_ALL)
            else:
                print(Back.RED)
                print (op)
                debit_solde+=float(op.data[op_lib.montant].replace(',','.'))
                print(Style.RESET_ALL)
            
        by_category , by_person = self.get_total_by_item(filtered_operations,montant_filter=NEGATIVE_FILTER)
        print("*********************\nCategories DEBIT\n********************")
        listing = sorted(by_category.items(), key=itemgetter(1))
        for key,value  in listing:
            print('{} {:,.2f} Eur'.format(key,value))
        print("*********************\nPersons DEBIT\n********************")
        listing = sorted(by_person.items(), key=itemgetter(1))
        for key,value  in listing:
            print('{} {:,.2f} Eur'.format(key,value))
            
        by_category , by_person = self.get_total_by_item(filtered_operations,montant_filter=POSITIVE_FILTER)
        print("*********************\nCategories CREDIT\n********************")
        listing = sorted(by_category.items(), key=itemgetter(1))
        for key,value  in listing:
            print('{} {:,.2f} Eur'.format(key,value))
        print("*********************\nPersons CREDIT\n********************")
        listing = sorted(by_person.items(), key=itemgetter(1))
        for key,value  in listing:
            print('{} {:,.2f} Eur'.format(key,value))
            
        print(Back.GREEN)
        print('{} : {:,.2f} Eur'.format('Credit   ', credit_solde))
        print(Back.RED)
        print('{} : {:,.2f} Eur'.format('Credit   ', debit_solde))
        print(Style.RESET_ALL)
        
        
        
        
        
        
    def get_total_by_item(self,operations,montant_filter = None):
        """
        Parameters
        **********
        operation: dict containing operations
        
        Returns
        *******
        (dict,dict) 1rst contains total by categories
                    2nd  contains total by persons
        """
        by_category={}
        by_person={}
        for op in operations.values():
            montant = float(op.data[op_lib.montant].strip().replace(',','.'))
            if montant_filter == NEGATIVE_FILTER and montant >=0. :  continue
            elif montant_filter == POSITIVE_FILTER and montant <=0. :  continue
            cat = op.category
            person = op.person
            if cat in by_category: by_category[cat]+=montant
            else: by_category[cat]=montant
            if person in by_person: by_person[person]+=montant
            else: by_person[person]=montant
                
        return by_category,by_person
                
                
                
    def pie(self):
        helps=('global', op_lib.data_label[op_lib.person],op_lib.data_label[op_lib.category])  
        cmd = self.ask("pie > ",helps=helps)
        if cmd == 'global':
            self.draw_global_pies()
        elif cmd == op_lib.data_label[op_lib.person]:
            self.draw_by_item_pies(op_lib.person)
        elif cmd == op_lib.data_label[op_lib.category]:
            self.draw_by_item_pies(op_lib.category)
        
        
    def draw_global_pies(self): 
        by_cat,by_pers = self.get_total_by_item(self.operations,montant_filter = NEGATIVE_FILTER)
        pies={'global category': by_cat} 
        self.draw_pies(pies)
        pies={'global person': by_pers} 
        self.draw_pies(pies)
        
        
        
    def draw_by_item_pies(self,item): 
        """
        Compute and display graphical pie account by person or caterories filtered by self.filters
        Parameters
        **********
        item: str, 'person' or 'category'
        """
        if item == op_lib.person:
            items=self.persons
            filter_item = op_lib.person
        elif item == op_lib.category:
            items=self.categories
            filter_item = op_lib.category
            
        pies=dict()
        old_filters = self.filters
        if items!=None:
            for item in items:
                self.filters=dict()
                if filter_item != None:
                    self.filters[op_lib.data_label[filter_item]]=item
                filtered_operations = self.get_filtered_operations()
                by_cat,by_pers = self.get_total_by_item(filtered_operations,montant_filter = NEGATIVE_FILTER)
                if filter_item == op_lib.person:
                    totals = by_cat
                elif filter_item == op_lib.category:
                    totals = by_pers
                if len(totals) > 1:
                    pies[item]=totals
            self.draw_pies(pies)    
        self.filters = old_filters
            
            
            
    def draw_pies(self,pies):                    
        """
        Display pies with matplotlib
        Parameters
        **********
        pies: dict. key: title, value dict : key item ,  value montant 
        """
        nb_plot = len(pies)
        if nb_plot == 0:
            return
        plot_id = 0
        cmap = plt.cm.hsv
        if nb_plot > 1 :
            nb_row = math.ceil((math.sqrt(nb_plot)))
            nb_line = nb_row-1
            while nb_line * nb_row < nb_plot:
                nb_line+=1
            f, axarr = plt.subplots(nb_line,nb_row)
        
        for key,totals in pies.items():    
            total = sum(totals.values())
            totals = { k : (v/total*100) for k,v in totals.items() }
            colors = cmap(np.linspace(0., 1., len(totals)))
            if nb_plot == 1 :
                plt.pie(list(totals.values()), colors=colors,labels=list(totals.keys()), autopct='%1.1f%%', shadow=True, startangle=90)
            else:
                line = int(plot_id/nb_row)
                row = plot_id%nb_row
                axarr[line,row].pie(list(totals.values()),colors=colors, labels=list(totals.keys()), autopct='%1.1f%%', shadow=True, startangle=90)
                total_str = '{:,.2f} Eur'.format(total)
                axarr[line,row].set_title(key+" " + str(total_str))
                plot_id+=1
            # Set aspect ratio to be equal so that pie is drawn as a circle.
            plt.axis('equal')
        plt.show()
        
        
            
    def manage_filters(self):
        """
        list, add and suppress filter from self.filters
        """
        while True:
            try: # 
                helps={'list': 'list active filters', 'add': 'add filter', "suppress": 'suppress filter'} 
                cmd=self.ask('filters > ', helps=helps)   
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
                    self.filters[item]=new_value
                elif cmd == 'suppress':
                    reponses=dict()
                    for intem,value in list(self.filters.items()):
                        reponses[intem] =  value
                    if len(reponses)>0:
                        item = self.ask("Enter item  to suppress > ",  helps=reponses)
                        try:
                            del self.filters[item]
                            print(item, 'suppressed')
                        except: print("Could not suppress this filter")
                    else: print('no acvite filter')
                    
                elif cmd == 'list':
                    print('activate filters list:')
                    print('----------------------')
                    for item,value in self.filters.items():
                        print('{} {}'.format(item,value))
                    
            except UserInterrupt:
                break
    def financial(self):
        """
        Get financial information, graphs, balance ...
        """
        try:
            while True:
                try:
                    helps={'list': 'list filtered operations', 'pie': 'draw pie', 'balance': 'get balance for current filters', "filters": 'add/suppress filters'} 
                    cmd=self.ask('financial review > ', helps=helps)   
                    if cmd == 'balance':
                        self.balance()
                    elif cmd == 'pie':
                        self.pie()
                    elif cmd == 'list':
                        result = self.get_filtered_operations()
                        print (result)
                    elif cmd == 'filters':
                        self.manage_filters()
                            
                        
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
                                    op.category=self.ask('    category?: ',default=op.category,helps=self.categories)
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
                                filtered_operations = self.get_filtered_operations()
                                print(filtered_operations)
                                
                            
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
        if self.input_file== None:
            print("Not input csv file. Open it first with open_csv command")
            return 
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
        
