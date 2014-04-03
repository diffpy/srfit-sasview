"""
Class for making sure all category stuff is installed
and works fine.

Copyright (c) Institut Laue-Langevin 2012

@author kieranrcampbell@gmail.com
@modified by NIST/MD sasview team
"""

import os
import sys
import shutil
import json
from collections import defaultdict

USER_FILE = 'serialized_cat.json'

class CategoryInstaller:
    """
    Class for making sure all category stuff is installed

    Note - class is entirely static!
    """


    def __init__(self):
        """ initialization """

    @staticmethod
    def _get_installed_model_dir():
        """
        returns the dir where installed_models.txt should be
        """
        import sans.dataloader.readers
        return sans.dataloader.readers.get_data_path()

    @staticmethod
    def _get_models_py_dir():
        """
        returns the dir where models.py should be
        """
        import sans.perspectives.fitting.models
        return sans.perspectives.fitting.models.get_model_python_path()
    
    @staticmethod
    def _get_default_cat_file_dir():
        """
        returns the dir where default_cat.j should be
        """
        # The default categories file is usually found with the code, except
        # when deploying using py2app (it will be in Contents/Resources), or
        # py2exe (it will be in the exec dir).
        import sans.sansview
        cat_file = "default_categories.json"
        
        possible_cat_file_paths = [
            os.path.join(os.path.split(sans.sansview.__file__)[0], cat_file),           # Source
            os.path.join(os.path.dirname(sys.executable), '..', 'Resources', cat_file), # Mac
            os.path.join(os.path.dirname(sys.executable), cat_file)                     # Windows
        ]

        for path in possible_cat_file_paths:
            if os.path.isfile(path):
                return os.path.dirname(path)
            
        raise RuntimeError('CategoryInstaller: Could not find folder containing default categories')

    @staticmethod
    def _get_home_dir():
        """
        returns the users sansview config dir
        """
        return os.path.join(os.path.expanduser("~"), ".sasview")

    @staticmethod
    def _regenerate_model_dict(master_category_dict):
        """
        regenerates self.by_model_dict which has each model name as the key
        and the list of categories belonging to that model
        along with the enabled mapping
        returns tuplet (by_model_dict, model_enabled_dict)
        """
        by_model_dict = defaultdict(list)
        model_enabled_dict = defaultdict(bool)
        
        for category in master_category_dict:
            for (model, enabled) in master_category_dict[category]:
                by_model_dict[model].append(category)
                model_enabled_dict[model] = enabled
    
        return (by_model_dict, model_enabled_dict)


    @staticmethod
    def _regenerate_master_dict(by_model_dict, model_enabled_dict):
        """
        regenerates master_category_dict from by_model_dict 
        and model_enabled_dict
        returns the master category dictionary
        """
        master_category_dict = defaultdict(list)
        for model in by_model_dict:
            for category in by_model_dict[model]:
                master_category_dict[category].append(\
                    (model, model_enabled_dict[model]))
        
        return master_category_dict

    @staticmethod
    def get_user_file():
        """
        returns the user data file, eg .sasview/serialized_cat.json
        """
        return os.path.join(CategoryInstaller._get_home_dir(),
                            USER_FILE)

    @staticmethod
    def get_default_file():
        """
        returns the path of the default file
        e.g. blahblah/default_categories.json
        """
        return os.path.join(\
            CategoryInstaller._get_default_cat_file_dir(), "default_categories.json")
        
    @staticmethod
    def check_install(homedir = None, model_list=None):
        """
        the main method of this class
        makes sure serialized_cat.json exists and if not
        compile it and install
        :param homefile: Override the default home directory
        :param model_list: List of model names except customized models
        """
        #model_list = []
        default_file = CategoryInstaller.get_default_file()
        serialized_file = None
        master_category_dict = defaultdict(list)
        if homedir == None:
            serialized_file = CategoryInstaller.get_user_file()
        else:
            serialized_file = os.path.join(homedir, USER_FILE)
        if os.path.isfile(serialized_file):
            cat_file = open(serialized_file, 'rb')
        else:
            cat_file = open(default_file, 'rb')
        master_category_dict = json.load(cat_file)
#        master_category_dict = pickle.Unpickler(cat_file).load()
        (by_model_dict, model_enabled_dict) = \
                CategoryInstaller._regenerate_model_dict(master_category_dict)
        cat_file.close()
        add_list = model_list
        del_name = False
        for cat in master_category_dict.keys():
            for ind in range(len(master_category_dict[cat])):
                model_name, enabled = master_category_dict[cat][ind]
                if model_name not in model_list:
                    del_name = True 
                    try:
                        by_model_dict.pop(model_name)
                        model_enabled_dict.pop(model_name)
                    except:
                        pass
                else:
                    add_list.remove(model_name)
        if del_name or (len(add_list) > 0):
            for model in add_list:
                model_enabled_dict[model]= True
                by_model_dict[model].append('Uncategorized')
    
            master_category_dict = \
                CategoryInstaller._regenerate_master_dict(by_model_dict,
                                                          model_enabled_dict)
            
            json.dump( master_category_dict,
                         open(serialized_file, 'wb') )
            
            try:
                #It happens only in source environment
                shutil.copyfile(serialized_file, default_file)
            except:
                pass
        
