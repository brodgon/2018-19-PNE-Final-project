import http.client
import json


HOSTNAME = 'rest.ensembl.org'
METHOD = "GET"
ENDPOINT = "/info/species?content-type=application/json"
ENDPOINT_K = "/info/assembly/"


headers = {'User-Agent': 'http-client'}


def connect_ensembl_karyotype(ENDPOINT_K):
    conn = http.client.HTTPSConnection(HOSTNAME)
    specie= input("Introduce specie: ")
    conn.request(METHOD, ENDPOINT_K+specie+"?content-type=application/json", None, headers)
    r1 = conn.getresponse()
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)

    text_json = r1.read().decode("utf-8")
    conn.close()
    Karyotype = json.loads(text_json)
    chromosomes = Karyotype['top_level_region']


    return chromosomes


def connect_ensembl_species(ENDPOINT):
    conn = http.client.HTTPSConnection(HOSTNAME)
    conn.request(METHOD, ENDPOINT, None, headers)
    r1 = conn.getresponse()
    print()
    print("Response received: ", end='')
    print(r1.status, r1.reason)

    text_json = r1.read().decode("utf-8")
    conn.close()
    specie = json.loads(text_json)
    return specie


def get_info_species(species_json):
    info =[]
    for i in species_json["species"]:
        info.append(i)
    species_Name = []
    for i in range(len(info)):
        species_Name.append(info[i]["display_name"])

    return species_Name

species_json = connect_ensembl_species(ENDPOINT)
info = get_info_species(species_json)
print("Available species:")
for i in info:
    print("\t", i, end="\n")
karyotype = connect_ensembl_karyotype(ENDPOINT_K)

chromosomes_name = []
for i in range(len(karyotype)):
    chromosomes_name.append(karyotype[i]["name"])
chromosomes_length = []
for i in range(len(karyotype)):
    chromosomes_length.append(karyotype[i]["length"])
print("The karyotype for the specie is:")
for i in chromosomes_name:
    print("\t", i, end="\n")
number = int(input("Chromosomes number info:"))
print("The length of your chromosome is: {}".format(chromosomes_length[number-1]))







