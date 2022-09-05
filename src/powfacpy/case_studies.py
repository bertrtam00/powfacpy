import sys
sys.path.insert(0,r'.\src')
import powfacpy

class PFStudyCases(powfacpy.PFBaseInterface):
  language = powfacpy.PFBaseInterface.language

  def __init__(self,app):
    super().__init__(app)
    self.active_grids = None
    self.parameter_values = {}
    self.parameter_paths = {}
    self.delimiter = " "
    self.hierarchy = []
    self.study_cases = []
    # ToDo base case/scen/var to copy or only base case
    self.parent_folder_study_cases = powfacpy.PFTranslator.get_default_study_case_folder_name(
      self.language)
    self.parent_folder_scenarios = powfacpy.PFTranslator.get_default_operation_scenario_folder_path(
      self.language)
    self.parent_folder_variations = powfacpy.PFTranslator.get_default_variations_folder_path(
      self.language)
    # Options  
    self.add_scenario_to_each_case = True
    self.add_variation_to_each_case = False
    self.consecutively_number_case_names = False
    self.anonymous_parameters = [] # Paramters of which names are not used 
    # in folder/case names (only their values are used)

  def create_cases(self):
    """Create study cases (and corresponding scenarios/variations)
    Iterates through all cases and creates study cases (and folders
    according to 'hierarchy') using parameter-value strings for the
    study cases (and folder names). 
    """
    number_of_cases = len(next(iter(self.parameter_values.values())))
    for case_num in range(number_of_cases):
      folder_path = self.get_folder_path(case_num)
      parameter_values_string = self.get_case_params_value_string(
        case_num,omitted_parameters=self.hierarchy) 
      if self.consecutively_number_case_names:
        parameter_values_string = str(case_num) + " " + parameter_values_string    
      self.study_cases.append(
        self.create_study_case(parameter_values_string,folder_path))
      self.activate_grids(case_num)
      if self.add_scenario_to_each_case:
        scen = self.create_scenario(parameter_values_string,folder_path)
      if self.add_variation_to_each_case:
        self.create_variation(parameter_values_string,folder_path)
      self.set_parameters(case_num)
      scen.Save()

  def get_folder_path(self,case_num):
    """Returns the folder path of a case.
    The path corresponds to parameter-value pairs specified
    in 'hierarchy'. 
    """
    if self.hierarchy:
      folder_path = ""
      for par_name in self.hierarchy:
        add_to_string = str(
          self.get_value_of_parameter_for_case(par_name,case_num)) + "\\"
        if not par_name in self.anonymous_parameters: 
          add_to_string = par_name + "_" + add_to_string
        folder_path += add_to_string
      return folder_path[:-1] # discard last "\\""
    else:
      return None

  def get_value_of_parameter_for_case(self,par_name,case_obj_or_case_num):
    """Returns a parameter value for a certain case.
    Arguments:
      par_name: Parameter name (string)
      case_obj_or_case_num: Either the case number (int) or
        a study case PF object (then the case number/index is derived first)

    Note that the values in 'parameter_values' can be 
      - a list/tuple where each element corresponds to a case number
      - or a single value which is used for all cases
    """
    case_num = self.handle_case_input(case_obj_or_case_num)
    values = self.parameter_values[par_name]
    if isinstance(values,(list,tuple)):
      return values[case_num]
    else:
      return values

  def handle_case_input(self,case_obj_or_case_num):
    """Accepts PF study case object or integer.
    If the input is a PF object, the corresponding case number is returned,
    else simply the input (integer) is returned.   
    """
    if not isinstance(case_obj_or_case_num,int):
      return self.study_cases.index(case_obj_or_case_num)
    else:
      return case_obj_or_case_num  

  def get_case_params_value_string(self,case_obj_or_case_num,
    omitted_parameters=None,
    delimiter=None,
    equals_symbol=None,
    anonymous_parameters=None):
    """Returns the parameter-value string for a case name.
    The string contains those parameters that are not in
    'hierarchy' (because these are used for the folder names).
    """
    case_num = self.handle_case_input(case_obj_or_case_num)
    if not delimiter:
      delimiter = self.delimiter
    if not equals_symbol:
      equals_symbol = "_"   
    parameter_values_string = ""
    for par_name in self.parameter_values:
      if omitted_parameters is None or par_name not in omitted_parameters:
        add_to_string = str(
          self.get_value_of_parameter_for_case(par_name,case_num)) + delimiter
        if anonymous_parameters is None:
          if par_name not in self.anonymous_parameters:
            add_to_string = par_name + equals_symbol + add_to_string
        elif par_name not in anonymous_parameters:
          add_to_string = par_name + equals_symbol + add_to_string 
        parameter_values_string += add_to_string
    return parameter_values_string[:-len(delimiter)] # discard last delimiter

  def create_study_case(self,parameter_values_string,folder_path):
    """Creates a study case with the name 'parameter_values_string'
    in the folder corresponding to 'folder_path' (this parth is 
    relativ to 'parent_folder_study_cases)
    """
    if folder_path:
      parent_folder = self.create_directory(folder_path,
        parent_folder=self.parent_folder_study_cases)
    else:
      parent_folder = self.parent_folder_study_cases
    study_case_obj = self.create_in_folder(parent_folder,
      parameter_values_string+".IntCase")
    study_case_obj.Activate()
    return study_case_obj

  def create_scenario(self,parameter_values_string,folder_path): 
    """Creates a scenario with the name 'parameter_values_string'
    in the folder corresponding to 'folder_path' (this parth is 
    relativ to 'parent_folder_scenarios)
    """
    if folder_path:
      parent_folder = self.create_directory(folder_path,
        parent_folder=self.parent_folder_scenarios)
    else:
      parent_folder = self.parent_folder_scenarios       
    scenario_obj = self.create_in_folder(parent_folder,
      parameter_values_string+".IntScenario")
    scenario_obj.Activate()
    scenario_obj.Save()
    return scenario_obj

  def create_variation(self,parameter_values_string,folder_path):
    """Creates a variation with the name 'parameter_values_string'
    in the folder corresponding to 'folder_path' (this path is 
    relativ to 'parent_folder_variations)
    """ 
    if folder_path:
      parent_folder = self.create_directory(folder_path,
        parent_folder=self.parent_folder_variations)
    else:
      parent_folder = self.parent_folder_variations 
    variation_obj = self.create_in_folder(parent_folder,
      parameter_values_string+".IntScheme")
    variation_obj.NewStage(parameter_values_string,0,1)
    variation_obj.Activate()
    return variation_obj

  def activate_grids(self,case_num):
    """Activate the corresponding grids of a study case.
    If 'active_grids' is a list/tuple, the elements correspond to
    each study case. If multiple grids are active, list/tuples can be 
    used in the elements in 'active_grids'. 
    If 'active_grid' is not a list/tuple, than one gird will be used
    for all cases.
    The grids can be thir paths or PF objects.
    """
    if isinstance(self.active_grids,(list,tuple)):
      grids = self.active_grids[case_num]
      if not isinstance(grids,(list,tuple)):
          grids = [grids]
      for grid in grids:
          grid = self.handle_single_pf_object_or_path_input(grid)
          grid.Activate()
    elif self.active_grids:
      grid = self.handle_single_pf_object_or_path_input(self.active_grids)
      grid.Activate() 

  def set_parameters(self,case_obj_or_case_num):
    """Set the parameters according to paths specified in 'parameter_paths'
    and values specified in 'parameter_values'. 
    """
    case_num = self.handle_case_input(case_obj_or_case_num)
    for par_name,path in self.parameter_paths.items():
      self.set_attr_by_path(path,
        self.get_value_of_parameter_for_case(par_name,case_num))  

  def get_study_cases(self,conditions):
    """Retrieve study case objects depending on parameter values.
    Arguments:
      conditions: A dictionary with
        keys: parameter names
        values: lambda function with boolean return value depending on 
          parameter (key)
    Returns the study case objects whose parameters fullfill the conditions.

    Example:
      get_study_cases({"par1": lambda x: x == 2, "par2": lambda x: x>0})
        This returns the study cases for which 'par1' equals 2 and 'par2' is 
        positive.       
    """
    cases = []
    for case_num,case_obj in enumerate(self.study_cases):
      conditions_fullfiled = True
      for parameter,condition in conditions.items():
        if not condition(self.get_value_of_parameter_for_case(parameter,case_num)):
          conditions_fullfiled = False
          break
      if conditions_fullfiled:
        cases.append(case_obj)
    return cases



  

