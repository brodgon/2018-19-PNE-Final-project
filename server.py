# We are importing all modules we will use later
import http.client
import json
import http.server
import socketserver
from Seq import Seq

# Establishing the port and allowing reusing it
PORT = 8000
socketserver.TCPServer.allow_reuse_address = True

# We are declaring the hostname (from where we will get all information); the method(get)
# and all the endpoints in order to get the information for our functions
HOSTNAME = 'rest.ensembl.org'
METHOD = "GET"
endpoint_species = "/info/species?content-type=application/json"
ENDPOINT_K = "/info/assembly/"
endpoint_gene = "/lookup/symbol/homo_sapiens/"
endpoint_Sequence = "/sequence/id/"
endpoint_infogene = "/overlap/id/"
endpoint_genelist = "/overlap/region/human/"

headers = {'User-Agent': 'http-client'}

# Now, I'm defining functions in order to connect to the host easily in the main function

# The following function allows us to connect and get species info


def connect_ensembl_species(endpoint):
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, endpoint, None, headers)
    r1 = conn.getresponse()
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)
    text_json = r1.read().decode("utf-8")
    conn.close()
    specie = json.loads(text_json)
    return specie


# The following function allows us to get the karyotype for any specie


def connect_ensembl_karyotype(specie):
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, ENDPOINT_K+specie+"?content-type=application/json", None, headers)
    r1 = conn.getresponse()
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)
    text_json = r1.read().decode("utf-8")
    conn.close()
    karyotype = json.loads(text_json)
    return karyotype

# gene_id will help us to "translate" the name the user will introduce for the gene to the 'ensembl name'


def gene_id(gene):
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, endpoint_gene + gene + "?expand=1;content-type=application/json", None, headers)
    r1 = conn.getresponse()
    print("Response received: ", end='')
    print(r1.status, r1.reason)
    text_json = r1.read().decode("utf-8")
    conn.close()
    gene_information = json.loads(text_json)
    if 'id' in gene_information:
        identification = gene_information['id']
    else:
        identification = '0'
    return identification

# This function will return the sequence for any gene


def sequence_gene(gene_ident):
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, endpoint_Sequence + gene_ident + "?content-type=application/json", None, headers)
    r1 = conn.getresponse()
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)
    text_json = r1.read().decode("utf-8")
    conn.close()
    sequence_info = json.loads(text_json)
    gene_sequence = sequence_info['seq']
    return gene_sequence

# From gene_info we will obtain the information we want from the gene


def gene_info(gene):
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, endpoint_infogene + gene + "?feature=gene;content-type=application/json", None, headers)
    r1 = conn.getresponse()
    print("Response received: ", end='')
    print(r1.status, r1.reason)
    text_json = r1.read().decode("utf-8")
    conn.close()
    info = json.loads(text_json)
    return info

# With this last function we are getting all the genes from the region of a chromosome


def gene_list(chromo, start, end):
    finish_endpoint = "?feature=gene;feature=transcript;feature=cds;feature=exon;content-type=application/json"
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, endpoint_genelist + chromo + ":"+start+"-"+end + finish_endpoint, None, headers)
    r1 = conn.getresponse()
    print("Response received: ", end='')
    print(r1.status, r1.reason)
    text_json = r1.read().decode("utf-8")
    conn.close()
    info = json.loads(text_json)
    return info


class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path

        print("GET Received")
        print("Request line: " + self.requestline)
        print("     Cnd:  " + self.command)
        print("Path:    " + path)

        # creating this to obtain the command for the action the user wants to carry
        command = path.split('?')
        command = command[0]

        # We are declaring an empty dictionary to create the json object if the user decides so
        dictionary = {}
        # Now we declare some empty variables in order to avoid "Unbound local error" exception
        content = ""
        species_names = ""
        title_species = ""
        chromosomes_name = ""
        specie_title = ""
        title_length = ""
        total_length = ""
        sequence = ''
        title_gene = ''
        information = ''
        title = ''
        info = ''
        gene_inf = ''
        genelist = ''
        # If path is 'empty' the main page will be opened
        if path == "/":
            with open("main_page.html", "r") as c:
                content = c.read()
        # If the user chooses to obtain the species it will enter this clause

        elif "/listSpecies" == command:
            species_json = connect_ensembl_species(endpoint_species)
            info = []
            for i in species_json["species"]:
                info.append(i)
            if "limit" in path:  # if the users type a limit or access the function from th main page 'limit' is shown
                limit = ''  # declaring variable in case it is not introduced
                values = path.strip('/listSpecies?')  # getting the parameters
                parameters = values.split('&')
                if "json=1" in parameters:  # we don't care now about json
                    parameters.remove('json=1')
                limit += parameters[0].strip('limit=')  # declaring gene as the parameter we want
                # Now we have to deal with all possible entries we could find
                if limit == '':  # if the user comes from the main page and do not introduce a limit, it will be empty
                    title_species += "Showing all available species:" + "\n"
                    for i in range(len(info)):
                        species_names += str(i+1)+".) " + info[i]['display_name'] + " also known as "+info[i]['common_name'] + '<br>'
                        dictionary[i] = [info[i]['display_name'], info[i]['common_name']]
                elif not limit.isdigit():  # if the user introduce something that is not a POSITIVE integer is not valid
                    title_species += "Cannot display information"
                    species_names = "Limit must be a positive integer number"
                    dictionary['error'] = species_names
                else:  # the third case is a positive integer number for limit, which is the only option valid
                    limit = int(limit)
                    # all species available are stored in info
                    if limit > len(info):
                        # if the number introduced is bigger than the species available, info cannot be shown
                        title_species += "Cannot show more than " + str(len(info))
                        species_names = "Try again with an integer between 0 and " + str(len(info))
                        dictionary['error'] = species_names
                    else:  # info will only be shown if the limit is smaller than the available species
                        title_species += "We will show " + str(limit) + " of " + str(len(info)) + " species available:"
                        # with the following loop all species will be introduced in an ordered way into:
                        # species name: For introducing it in the html file if json is not in path (IT MUST BE STR)
                        # dictionary: if json is in path, it will send the dictionary instead of the string
                        for i in range(limit):
                            species_names += str(i + 1) + ".) " + info[i]['display_name'] + " also known as " + \
                                             info[i]['common_name'] + '<br>'
                            dictionary[i] = [info[i]['display_name'], info[i]['common_name']]
            else:
                # if limit is not in path (the user introduced the path manually) all species will be shown
                title_species = "Showing all available species:"
                # again the species will be added in the string, for html and in dictionary for json
                for i in range(len(info)):
                    species_names += str(i + 1) + ".) " + info[i]['display_name'] + " also known as " + info[i][
                        'common_name'] + '<br>'
                    dictionary[i] = [info[i]['display_name'], info[i]['common_name']]

        elif "/karyotype" == command:
            specie = ''  # declaring variable in case it is not introduced
            values = path.lstrip('/karyotype?')
            # getting the parameters
            parameters = values.split('&')
            if "json=1" in parameters:  # we don't care now about json
                parameters.remove('json=1')
            if len(parameters) < 1:  # we are now getting the specie name
                specie = ''
            else:
                specie_list = parameters[0].split('=')
                specie += specie_list[1]
            if specie == '':  # if it is empty we cannot hold any operation
                specie_title = 'Error'
                chromosomes_name += 'Please introduce a specie'
                dictionary["error"] = "Specie must be specified"
            else:  # if sth is introduced:
                # we are replacing + of the input with _ for the program to read it easily if specie has two names
                specie = specie.replace('+', '_')
                # we call the function to get the karyotype of the specie we want
                specie_karyotype = connect_ensembl_karyotype(specie)
                # we define the title for the html file
                specie_title += specie
                # we obtain now the chromosomes from the karyotype (usually numbers)
                if 'karyotype' in specie_karyotype:
                    karyotype = specie_karyotype['karyotype']  # taking the chromosomes from the specie_karyotype dict
                    if karyotype == []:
                        chromosomes_name = 'Karyotype not available' + '<br>' + 'Please try again'
                        dictionary['error'] = 'Could not find information'
                    else:  # with this loop we are putting each chromosome in an 'ordered way'
                        for i in range(len(karyotype)):
                            chromosomes_name += karyotype[i] + '<br>'
                            dictionary[i] = karyotype[i]
                # if karyotype is not available an error message is displayed
                else:
                    chromosomes_name += "Sorry,no information found for " + specie_title
                    dictionary['error'] = chromosomes_name

        elif "/chromosomeLength" == command:
            specie = ''  # variables declared here to avoid unbound local error
            number = ''  # also used in case the user does not introduce them
            # now we obtain the parameters we want as they may be introduced in the order we want
            values = path.lstrip('/chromosomeLength').strip('?')  # we eliminate the 'chromosomelength'
            parameters = values.split('&')  # we are now creating a list with the parameters
            if 'json=1' in parameters:
                parameters.remove('json=1')
            if len(parameters) < 2:  # if the user just type manually (not from the main page) one parameter
                title_length = 'Error'  # is not possible to handle the operation
                total_length = 'Chromosomes and species MUST be both specified'
                dictionary['error'] = "Both chromosome and specie must be identified "
            elif len(parameters) == 2:
                for i in parameters:
                    if 'specie=' in i:
                        specie = i.split('=')
                        specie = specie[1]    # taking specie's name
                    elif 'chromo=' in i:
                        number = i.strip('chromo=')  # taking the chromosome number
                if specie == '' or number == '':  # if one or both of the parameters are empty
                    if specie == '' and number == '':  # both empty
                        title_length = 'Error'
                        total_length = 'Please introduce a specie and a chromosome'
                        dictionary['error'] = "Specie and chromosome must be introduced"
                    elif specie == '':  # specie empty
                        title_length = 'Error'
                        total_length = 'Please introduce a specie'
                        dictionary['error'] = "Specie must be introduced"
                    else:  # chromosome is empty
                        title_length = 'Error'
                        total_length = 'Please introduce a chromosome'
                        dictionary['error'] = "Chromosome must be introduced"
                else:  # if no one is empty
                    specie_karyotype = connect_ensembl_karyotype(specie)  # connect to ensembl and get karyotype
                    if 'top_level_region' in specie_karyotype:  # if the karyotype for the specie is found
                        main_kary = specie_karyotype['karyotype']   # we get the karyotype to examine its length
                        karyotype = specie_karyotype['top_level_region']  # from hare we will obtain its length
                        position_x = ""  # We need to handle with the last chromosomes of all karyotypes
                        position_mt = ""   # in case they are introduced with numbers (e.g human chromo 22 = x)
                        position_y = ""
                        for pos in range(len(main_kary)):
                            if main_kary[pos] == 'X':  # we give chromosomes X Y and MT a numerical position
                                position_x = pos + 1
                            elif main_kary[pos] == 'Y':
                                position_y = pos + 1
                            elif main_kary[pos] == 'MT':
                                position_mt = pos + 1
                        if number.isdigit():  # if chromosome is a number
                            if len(main_kary) >= int(number):  # if the number introduced is = or lower to the length
                                length = ""  # of the karyotype then its valid and we hold operations
                                for i in karyotype:  # we iterate over the karyotype dictionary to find the chromosome
                                    if i['name'] == number:
                                        length = i['length']
                                        break
                                    elif i['name'] == 'X' and number == str(position_x):
                                        print(i['name'])
                                        length = i['length']
                                        break
                                    elif i['name'] == 'Y' and number == str(position_y):
                                        length = i['length']
                                        break
                                    elif i['name'] == 'MT' and number == str(position_mt):
                                        length = i['length']
                                        break
                                    else:
                                        length = 'Not found'
                                title_length += "Length for chromosome " + str(number) + " of " + specie + " is "
                                total_length += str(length)
                                dictionary[number] = "Length for your chromosome "+total_length

                            elif len(main_kary) < int(number):  # if number is bigger than the length of karyotype
                                title_length += 'Chromosome not found '  # Can´t hold operation
                                total_length += 'Only numbers up to ' + str(len(main_kary)) + ' available'
                                dictionary['error'] = title_length + total_length

                        else:  # if the chromosome introduced is alpha
                            # we first have to see if it is one of x, y or MT (possible letter chromosome)
                            if number.lower() == 'x' or number.lower() == 'y' or number.lower() == 'mt':
                                length = ''  # if it one of those we will look up for its length
                                for i in karyotype:  # we iterate over the dictionary and look for that chromosome
                                    if i['name'] == number.upper():
                                        print(i['name'])
                                        length = i['length']
                                        break
                                title_length += "Length for chromosome: "+number
                                total_length += str(length)
                                dictionary['length'] = total_length

                            else:  # if is any other thing an error will be shown
                                title_length += "Chromosome must be number "
                                total_length += "Try again with some number between 0 and " + str(len(main_kary))
                                dictionary['error'] = title_length + total_length
                    else:  # this will happen if the karyotype is not available
                        title_length += "Can´t find karyotype for "+specie
                        total_length += "Unknown"
                        dictionary[total_length] = title_length

        # MEDIUM LEVEL: human genome information
        #
        elif "/geneSeq" == command:  # we obtain the sequence of a concrete gene
            gene = ''  # declaring variable in case it is not introduced
            values = path.strip('/geneSeq?')  # getting the parameters
            parameters = values.split('&')
            if "json=1" in parameters:  # we don't care now about json
                parameters.remove('json=1')
            if len(parameters) < 1:
                gene = ''
            else:
                gene += parameters[0].strip('gene=')  # declaring gene as the parameter we want
            if gene == '':  # if it is empty we cannot hold any operation
                gene_inf = 'Error'
                sequence += 'Please introduce a gene'
                dictionary["error"] = "Gene must be specified"
            else: # if sth is introduced:
                # the goal of this function is to transform the gene from common name (e.g frat1) to the ensembl name
                id_info = gene_id(gene)  # the function will return the ensembl name or 0 if the gene is not ok
                if id_info == '0':  # if the gene is not found (0) an error message will be saved
                    gene_inf = 'Info not found for gene ' + gene
                    sequence += 'Not possible to calculate sequence' + '<br>' + 'Try again with a valid gene'
                    dictionary["error"] = "not found"
                else:  # if the gene is available (we acquire the ensembl name) we obtain the  DNA sequence
                    seq = sequence_gene(id_info)  # we obtain the sequence connecting to this function
                    for i in range(len(seq)):
                        if i % 100 == 0:  # displaying the sequence in the web in a tidy way for the html file
                            sequence = sequence + seq[i:i+100] + '<br>'
                    gene_inf = "Displaying sequence for gene " + gene  # this will be the tile for the html file
                    dictionary["Sequence"] = seq  # the dictionary for json is stored here
                    print(sequence)
                    print(dictionary)
        elif "/geneInfo" == command:  # with this path  we want to obtain some information of each gene
            gene_input = ''  # declaring variable in case it is not introduced
            values = path.strip('/geneInfo?')  # getting the parameters
            parameters = values.split('&')
            if "json=1" in parameters:  # we don't care now about json
                parameters.remove('json=1')
            if len(parameters) < 1:
                gene_input = ''
            else:
                gene_input += parameters[0].strip('gene=')
            if gene_input == '':  # if it is empty we cannot hold any operation
                title_gene = 'Error'
                information += 'Please introduce a gene'
                dictionary["error"] = "Gene must be specified"
            else: # if sth is introduced:
                gene_name = gene_id(gene_input)  # we call this function to obtain the ensembl name
                if gene_name == '0':  # if the gene is not available (0) an error message is displayed
                    title_gene = 'Info not found for gene ' + gene_name
                    information = 'Not possible to find information' + '<br>' + 'Try again with a valid gene'
                    dictionary["error"] = "not found"
                else:  # if the gene is info we will look up for information
                    info = gene_info(gene_name)
                    # the variable info stores a dictionary with all the information for the gene the user wills
                    # we also obtain genes for its parents genes
                    gene_ident = ""
                    start = ""
                    end = ""  # variables declared now as empty variables to avoid Unbound local error exception
                    chromosome = ""
                    length = ""
                    for i in range(len(info)):
                        # we look up for the information for that SPECIFIC gene
                        if info[i]['id'] == gene_name:
                            # we find the id, the start, the end and its length
                            gene_ident = str(info[i]['id'])
                            start = str(info[i]['start'])
                            end = str(info[i]['end'])
                            chromosome = str(info[i]['seq_region_name'])
                            length = str(int(end)-int(start))
                            # break
                    # we store the information in the strings for the html and the json file
                    title_gene += 'Displaying information for gene ' + gene_input
                    information += 'Gene id: ' + gene_ident + '<br>' + 'Start: ' + start + '<br>'
                    information += 'End: ' + end + '<br>' + "Length: " + length + '<br>' + 'Chromosome: ' + chromosome
                    dictionary["Gene Id"] = gene_ident
                    dictionary["Start"] = start
                    dictionary["End"] = end
                    dictionary["Length"] = length
                    dictionary["Chromosome"] = chromosome
        elif "/geneCalc" == command:
            gene_intro = ''  # variable declared in case is empty
            values = path.strip('/geneCalc?')  # we are obtaining parameters
            parameters = values.split('&')
            if 'json=1' in parameters:  # now json is not necessary
                parameters.remove('json=1')
            if len(parameters) < 1:  # we are getting the gene info
                gene_intro = ''  # here it will enter only if 'gene=' is not in the command
            else:
                gene_intro += parameters[0].strip('gene=')
            if gene_intro == '':  # if no gene is introduced
                title = 'Error'
                info = 'Please introduce a valid gene'
                dictionary["error"] = "Gene must be specified"
            else:
                gene_identification = gene_id(gene_intro)  # we are getting the ensembl id
                if gene_identification == '0': # if the gene is not found in the ensembl firectory
                    title = 'Info not found for gene ' + gene_intro
                    info = 'Not possible to calculate sequence' + '<br>' + 'Try again with a valid gene'
                    dictionary["error"] = "not found"
                else:
                    seq = sequence_gene(gene_identification)   # obtaining the gene's sequence
                    sequence = Seq(seq)  # transforming it into an object to use the functions stored in Seq.py
                    length = sequence.len()  # getting its length
                    perc_a = sequence.perc("A")  # calculating percentages
                    perc_c = sequence.perc("C")
                    perc_g = sequence.perc("G")
                    perc_t = sequence.perc("T")
                    # storing the messages
                    info = "The length of the gene´s sequence is: " + str(length) + "<br>"
                    info += "     Percentage of Adenine (A):"+str(perc_a)+"%"+"<br>"
                    info += "     Percentage of Guanine (G): " + str(perc_g)+"%" + "<br>"
                    info += "    Percentage of Citosine (C):" + str(perc_c) + "%"+"<br>"
                    info += "     Percentage of Thymine (T): " + str(perc_t)+"%"
                    title = "Displaying sequence´s information for gene " + gene_intro + "("+gene_identification+")"
                    # creating dictionaries for json
                    dictionary["Total Length"] = length
                    dictionary["Percentage Adenine"] = perc_a
                    dictionary["Percentage Guanine"] = perc_g
                    dictionary["Percentage Citosine"] = perc_c
                    dictionary["Percentage Thymine"] = perc_t
        elif "/geneList" == command:
            # declaring variables in case they are empty
            chromo = ''
            start = ''
            end = ''
            values = path.split('/geneList?')  # getting the variables information as in previous function
            if len(values) > 1:
                values = values[1]
            else:
                values = values[0]
            parameters = values.split('&')
            if 'json=1' in parameters:
                parameters.remove('json=1')
            for i in parameters:
                if 'chromo=' in i:
                    chromo = i.strip('chromo=')
                elif 'end=' in i:
                    end = i.strip('end=')
                elif 'start=' in i:
                    start = i.strip('start=')
            if len(parameters) < 3:  # if we do not find 3 parameters an automatic error will be shown
                title += 'Error '
                genelist += 'The following parameters must be included: chromosome, start and end of region.  '
                dictionary['error'] = 'All parameters must be included'
            elif len(parameters) > 3:
                title += 'Error '
                genelist += 'Just the following parameters must be included: chromosome, start and end of region.  '
                dictionary['error'] = 'Only 3 parameters must be included'
            elif len(parameters) == 3:  # only will work with 3 parameters specified
                if chromo == '' or end == '' or start == '': # storing messages if we find them empty
                    if chromo == '':
                        title += 'Error '
                        genelist += 'Please introduce a value for chromosome '
                        dictionary['error'] = 'Chromosome must be specified'
                    elif start == '':
                        title += 'Error '
                        genelist += 'Please introduce a value for the start of region '
                        dictionary['error'] = 'The start of region must be specified'
                    elif end == '':
                        title += 'Error '
                        genelist += 'Please introduce a value for the end of region '
                        dictionary['error'] = 'The end of region must be specified'
                else:  # getting the list from the ensembl rest api
                    list_g = gene_list(chromo, start, end)
                    if 'error' in list_g:  # handling with the errors we can find
                        if 'No slice' in list_g['error']:
                            genelist = "Couldn't held operation" + "<br>"
                            genelist += "Try again using the following instructions"+"<br>"
                            genelist += "Chromo must be an integer number between 0-22 or X or Y or MT"+"<br>"
                            genelist += "Start number MUST BE LOWER than end"
                            title = "Information not found"
                        elif 'not understood' in list_g['error']:
                            genelist = "Couldn't held operation" + "<br>"
                            genelist += "Try again using the following instructions"+"<br>"
                            genelist += "Chromo must be an integer number between 0-22 or X or Y or MT"+"<br>"
                            genelist += "Start number MUST BE LOWER than end"
                            title = "Information not found"
                        else:
                            genelist = list_g['error'] + "<br>" + "Try again"
                            title = "INFORMATION NOT FOUND"
                        dictionary['error'] = "not found"
                    elif not list_g:  # if we cannot get a list
                        genelist = "Sorry couldn't find information"+"<br>"+"Try again please"
                        title = "NOT FOUND"
                        dictionary["error"] = "not found"
                    else:  # if we find a list without errors we will store it in an ordered way
                        genelist = ""
                        for i in range(len(list_g)):
                            genelist += str(i+1)+".) Gene: " + list_g[i]["id"]
                            dictionary[i] = {}
                            dictionary[i]["gene"] = list_g[i]['id']
                            if 'external_name' in list_g[i]:
                                genelist += "  Common name: " + list_g[i]['external_name'] + '<br>'
                                dictionary[i]["common name"] = list_g[i]['external_name']
                            else:
                                genelist += '<br>'
                        title = "Displaying genes for chromosome " + str(chromo)

        else:  # if any other command is asked
            with open("error.html", "r") as c:
                content = c.read()

        if "json=1" in path:  # if the json=1 parameter is included the user will receive a json object
            f = open("information.json", 'w') # we create a json file
            json.dump(dictionary, f)  # and insert the dictionary with the information
            f.close()
            g = open("information.json", 'r')  # the we will open that json fil
            content = g.read()  # declare it as our content
            content_type = 'application/json'  # and specified is json
        else:
            # if 'json=1' parameter is not included an html will appear with the information stored previously
            content_type = 'text/html'  # we will declare html
            if "/listSpecies" == command:
                with open("listSpecies.html", "r") as f:
                    content = f.read().format(title_species, species_names)
                    f.close()
            elif "/karyotype" == command:
                with open("karyotype.html", "r") as f:
                    content = f.read().format(specie_title, chromosomes_name)
                    f.close()
            elif "/chromosomeLength" == command:
                with open("chromosomelength.html", "r") as f:
                    content = f.read().format(title_length, total_length)
                    f.close()
            elif "/geneSeq" == command:
                with open("geneSeq.html", "r") as f:
                    content = f.read().format(gene_inf, sequence)
                    f.close()
            elif "/geneInfo" == command:
                with open("geneInfo.html", "r") as f:
                    content = f.read().format(title_gene, information)
                    f.close()
            elif "/geneCalc" == command:
                with open("geneCalc.html", "r") as f:
                    content = f.read().format(title, info)
                    f.close()
            elif "/geneList" == command:
                with open("geneList.html", "r") as f:
                    content = f.read().format(title, genelist)
                    f.close()

        # -- We want to generate a response message with the following command
        self.send_response(200)

        # --- define the content type and the header
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(str.encode(content)))

        # finish the header
        self.end_headers()

        # send the body of the response se message
        self.wfile.write(str.encode(content))


Handler = TestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:

    print("Serving at PORT", PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stopped by the user")
        httpd.server_close()
    except ConnectionAbortedError:
        print("Connection aborted")
print("")
print("Server Stopped")
