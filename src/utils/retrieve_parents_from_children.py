class ParentsFromChildrenRetriever:
    def __init__(self, actor_wikidata):
        """
        This function construct the dictionary that map each actor to a potential list of parents.
        
        :param actor_wikidata (pandas.DataFrame): The dataset containing actor information, including children and the label name for each actor.
        
        :return (dict): A dictionary mapping children's names to a list of parent names.
        """
        # init the dictionary
        self.child_to_parents = {}
        
        # iterate over all the rows of the wikidata actor dataframe.
        for _, row in actor_wikidata.iterrows():
            # for each child, affect the parent_name associated
            for child in row['children']:
                # check if the child is already present in the dictionary
                if child not in self.child_to_parents:
                    self.child_to_parents[child] = []
                parentName = row['actorLabel']
                # check if the parent is already present in the array of parent associated to the child ( evict duplicates)
                if parentName not in self.child_to_parents[child]:
                    self.child_to_parents[child].append(parentName)
        


    def find_parents_for_child_actor_name(self, child_actor_name):
        """
        This function retrieves all the parents of a given actor.

        :param child_actor_name (str): The name of the child actor whose parents are to be found.
        
        :return (List[str]): The list containing the parents of the child actor.
        """
        # Use the dictionary defined in this class to retrieve the parent list.
        return self.child_to_parents.get(child_actor_name, [])