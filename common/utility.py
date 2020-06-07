import hashlib
import json
import pickle


class Utility:
    @staticmethod
    def generate_hash_for_given_block(block):
        """ Returns the hash for the given block """
        # return '_'.join([str(block[key]) for key in block])
        copy_of_block_dict = block.__dict__.copy()
        copy_of_block_dict['transactions'] = [
            tx.to_ordered_dict() for tx in copy_of_block_dict['transactions']]
        return hashlib.sha256(json.dumps(copy_of_block_dict, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def pickle_save(where_to_save, what_data_to_save):
        """Save data using pickle module
        Arguments:
            :where_to_save: file path to save data
            :what_data_to_save: object/data
        """
        # open with 'with' keyword close reference file automatically, you don't have to close force fully
        with open(where_to_save, 'wb') as file_object:
            # save file as binary format
            pickle.dump(what_data_to_save, file_object)

    @staticmethod
    def pickle_read(fromwheretoread):
        """Read data using pickle module
        Arguments:
            :from_where_to_read: file path to read data
        """
        # open with 'with' keyword close reference file automatically, you don't have to close force fully
        with open(fromwheretoread, 'rb') as file_object:
            # returns file content
            return pickle.load(file_object)

    @staticmethod
    def json_save(where_to_save, what_data_to_save):
        """Save data using json module
        Arguments:
            :where_to_save: file path to save data
            :what_data_to_save: object/data
        """
        # open with 'with' keyword close reference file automatically, you don't have to close force fully
        with open(where_to_save, 'w') as file_object:
            # save file as binary format
            file_object.write(json.dumps(what_data_to_save))

    @staticmethod
    def json_read(fromwheretoread):
        """Read data using json module
        Arguments:
            :from_where_to_read: file path to read data
        """
        # open with 'with' keyword close reference file automatically, you don't have to close force fully
        with open(fromwheretoread, 'r') as file_object:
            # returns file content
            return json.load(file_object)
