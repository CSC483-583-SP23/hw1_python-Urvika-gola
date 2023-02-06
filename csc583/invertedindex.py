import re


class InvertedIndex:
    """
    Class InvertedIndex takes in a text file containing the DocID and words as input to create an inverted index
    It contains methods to calculate the query containing operations such as AND or/and OR
    Public Methods: read_txt_file, q5_1, q5_2, q5_3
    Private Methods: _parse_query, _create_inverted_index, _get_doc_id_from_line, _calculate_and, _calculate_or
    Author: Urvika Gola
    Course: CSC 583, Instructor - Mihai Surdeanu, TA - Shreya Nupur Shakya
    """

    def __init__(self, doc):
        """
        The constructor for InvertedIndex class
        :param doc: the document file containing documents
        """
        self.doc = doc

    def read_txt_file(self, input_file: str) -> list:
        """
        Read the text file line by line; and stores every line in a string array
        :param input_file: Docs.txt
        :return: a string array of non-empty lines
        """
        with open(input_file) as f:
            lines = [line.strip() for line in f.readlines() if len(line.strip()) != 0]
        if len(lines) == 0:
            assert False, "The document is empty, returning False."
        return lines

    def q5_1(self, query: str) -> list:
        """
        Method for Q5 Part 1
        :param query: the query to be executed e.g. schizophrenia AND drug
        :return: a list of resultant DocIDs e.g. ['Doc1', 'Doc4']
        """
        return self._parse_query(query)

    def q5_2(self, query: str) -> list:
        """
        Method for Q5 Part 2
        :param query: the query to be executed e.g. breakthrough OR new
        :return: a list of resultant DocIDs e.g. ['Doc1', 'Doc2', 'Doc3', 'Doc4']
        """
        return self._parse_query(query)

    def q5_3(self, query: str) -> list:
        """
        Method for Q5 Part 3
        Note: I would be removing the parentheses and prioritizing the AND operator followed by OR
        i.e. Precedence of AND then OR
        :param query: the query to be executed e.g. (drug OR treatment) AND schizophrenia
        :return: a list of resultant DocIDs e.g. ['Doc1', 'Doc2', 'Doc4']
        """
        return self._parse_query(query)

    def _parse_query(self, query: str) -> list:
        """
        A private method to parse query of any 3 types:
        1. schizophrenia AND drug
        2. breakthrough OR new
        3. (drug OR treatment) AND schizophrenia
        Note that for the 3rd type, the parentheses will be removed and "AND" operation will precede over "OR"
        :param query: the input query
        :return: a list of sorted DocIDs
        """

        lines = self.read_txt_file(self.doc)  # read the text file and create an array of lines
        inverted_index = self._create_inverted_index(lines)  # create an inverted index
        query = re.sub(r"[()]", "", query)  # remove any ( or ) parentheses from the query
        split_query = query.split()  # split the query on basis of space

        if len(split_query) < 3:
            print(f"Invalid query {query}, there should be minium 3 parts supplied, <'operand' 'operator' 'operand'>")
            return []

        store_intermediate_results = {}

        # first we will solve all the ANDs present in the query, if it's not present then we will check for ORs
        while len(split_query) > 1 and 'AND' in split_query:
            operator_idx = split_query.index('AND')  # note that the AND should be an upper case literal
            first_operand_result, second_operand_result = None, None
            if split_query[operator_idx - 1] in store_intermediate_results:
                first_operand_result = store_intermediate_results[split_query[operator_idx - 1]]
            if split_query[operator_idx + 1] in store_intermediate_results:
                second_operand_result = store_intermediate_results[split_query[operator_idx + 1]]
            try:
                intermediate_result = self._calculate_and(
                    first_operand_result if first_operand_result is not None else inverted_index[
                        split_query[operator_idx - 1]],
                    second_operand_result if second_operand_result is not None else inverted_index[
                        split_query[operator_idx + 1]])
            except KeyError as e:
                print(f"Invalid Query: The word '{e.args[0]}' is not in the documents, the query can't be calculated.")
                return []
            key = f"{split_query[operator_idx - 1]} {split_query[operator_idx]} {split_query[operator_idx + 1]}"
            store_intermediate_results[key] = intermediate_result
            split_query.insert(operator_idx + 2, key)
            del split_query[operator_idx - 1: operator_idx + 2]

        # second, we will solve all the ORs present in the query.
        while len(split_query) > 1 and 'OR' in split_query:
            operator_idx = split_query.index('OR')  # note that the OR should be an upper case literal
            first_operand_result, second_operand_result = None, None
            if split_query[operator_idx - 1] in store_intermediate_results:
                first_operand_result = store_intermediate_results[split_query[operator_idx - 1]]
            if split_query[operator_idx + 1] in store_intermediate_results:
                second_operand_result = store_intermediate_results[split_query[operator_idx + 1]]
            try:
                intermediate_result = self._calculate_or(
                    first_operand_result if first_operand_result is not None else inverted_index[
                        split_query[operator_idx - 1]],
                    second_operand_result if second_operand_result is not None else inverted_index[
                        split_query[operator_idx + 1]])
            except KeyError as e:
                print(f"Invalid Query: The word '{e.args[0]}' is not in the documents, the query can't be calculated.")
                return []
            key = f"{split_query[operator_idx - 1]} {split_query[operator_idx]} {split_query[operator_idx + 1]}"
            store_intermediate_results[key] = intermediate_result
            split_query.insert(operator_idx + 2, key)
            del split_query[operator_idx - 1: operator_idx + 2]
        return ["Doc" + str(value) for value in store_intermediate_results[split_query[0]]]

    def _create_inverted_index(self, lines: list) -> dict:
        """
        Private method to create the inverted index
        :param lines: the lines of the Docs.txt as a String Array
        :return: a dictionary containing the inverted index with key as the word and value as the posting list
        """
        doc_id_with_line = {}
        # {1: 'Doc1    breakthrough drug for schizophrenia', 2: 'Doc2    new approach for treatment of schizophrenia',
        # 3: 'Doc3    new hopes for schizophrenia patients', 4: 'Doc4    new schizophrenia drug'}
        inverted_index = {}

        for line in lines:
            doc_id = self._get_doc_id_from_line(line)  # the key is the Doc ID
            if doc_id:
                # ignore the lines from which we were unable to parse DocID e.g. "Doc    breakthrough for schizophrenia"
                doc_id_with_line[doc_id] = line

        for doc_id, line in doc_id_with_line.items():
            words = line.split()[1:]  # skip the first word as it must be the Doc identifier like 'Doc1'
            for word in words:
                if word not in inverted_index:
                    inverted_index[word] = [doc_id]
                elif word in inverted_index:
                    # append the doc_id if it's not present in the posting list,
                    # if it's already present, we will skip it as we don't want duplicates.
                    get_doc_ids = inverted_index[word]
                    if doc_id not in get_doc_ids:
                        inverted_index[word].append(doc_id)

        # sort the dictionary's value (posting list)
        sorted_inverted_index = {key: sorted(inverted_index[key]) for key in inverted_index}
        return sorted_inverted_index

    def _get_doc_id_from_line(self, line: str) -> int:
        """
        Get the number and index of this last digit so that after that the content of the line starts
        :param line: the line containing the docID and words e.g. "Doc40    new schizophrenia drug"
        :return: the integer part of the DocID eg, returns int 40 for "Doc40    new schizophrenia drug"
        """
        num = []
        for char in line:
            if char.isdigit():
                num.append(char)
            elif char == " ":
                return int(''.join(num)) if (len(num) > 0) else False
        # return false if no numeric digit was found in the line.
        return int(''.join(num)) if (len(num) > 0) else False

    def _calculate_and(self, list1: list, list2: list) -> list:
        """
        A private method to calculate AND operation between the two posting lists
        :param list1: first posting list
        :param list2: second posting list
        :return: a list containing the result of AND operation between the two posting lists
        """
        i, j = 0, 0  # to access indices i and j or list1 and list2 respectively
        output = []
        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                output.append(list1[i])
                i += 1
                j += 1
            elif list1[i] < list2[j]:
                i += 1
            else:
                j += 1
        return output

    def _calculate_or(self, list1: list, list2: list) -> list:
        """
        A private method to calculate OR operation between the two posting lists
        :param list1: first posting list
        :param list2: second posting list
        :return: a list containing the result of OR operation between the two posting lists
        """
        i, j = 0, 0  # to access indices i and j or list1 and list2 respectively
        output = []
        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                output.append(list1[i])
                i += 1
                j += 1
            elif list1[i] < list2[j]:
                output.append(list1[i])
                i += 1
            elif list1[i] > list2[j]:
                output.append(list2[j])
                j += 1
        while i < len(list1):
            output.append(list1[i])
            i += 1
        while j < len(list2):
            output.append(list2[j])
            j += 1
        return output
