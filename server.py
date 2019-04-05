import http.client
import json
import http.server
import socketserver
import termcolor

PORT = 8000
HOSTNAME = 'rest.ensembl.org'
METHOD = "GET"
ENDPOINT = "/info/species?content-type=application/json"
ENDPOINT_K = "/info/assembly/"


headers = {'User-Agent': 'http-client'}


def connect_ensembl_karyotype(ENDPOINT_K):
    conn = http.client.HTTPSConnection(HOSTNAME)
    specie = input("Introduce specie: ")
    specie = specie.replace(" ", "_")
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


class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET Received")
        print("Request line" + self.requestline)
        print("     Cnd:  " + self.command)
        print("Path:    " + self.path)

        termcolor.cprint(self.requestline, 'blue')
        if self.path == "/":
            with open("main_page.html", "r") as c:
                content = c.read()
        elif "/listSpecies" in self.path:
            species_json = connect_ensembl_species(ENDPOINT)
            info = get_info_species(species_json)
            if "limit" in self.path:
                limit = int(self.path[self.path.find("=")+1:])
                info1 = "We will show " + str(limit)+ " of " + str(len(info)) + " species available:"
                info2 = " "
                for num in range(limit):
                    info2 += "\t" + info[num] + "   " + "\n"
            else:
                info1 = "List of available species:" + "\n"
                info2 = " "
                for i in info:
                    info2 += "\t" + i + "\n"

            with open("listSpecies.html", "r") as f:
                content = f.read().format(info1,info2)
                f.close()

        # -- We want to generate a response message with the following command
        self.send_response(200)

        # --- Now we will define the content type and the header
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(content)))

        # We now finish the header
        self.end_headers()

        # We will now send the body of the response se message
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

print("")
print("Server Stopped")


"""species_json = connect_ensembl_species(ENDPOINT)
info = get_info_species(species_json)
print("Available species:")
for i in info:
    print("\t", i, end="\n")"""
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







