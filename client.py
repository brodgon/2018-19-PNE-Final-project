import http.client

# --- Connecting to the server (THE SERVER MUST BE RUNNING)
PORT = 8000
SERVER = 'localhost'

# --- Declaring some endpoints to get  the json
list_specie = ["/listSpecies?json=1","/listSpecies?limit=&json=1" , "/listSpecies?limit=15&json=1", "/listSpecies?json=1&limit=15","/listSpecies?limit=a&json=1"]
karyotype = ['/karyotype?specie=&json=1', '/karyotype?specie=mouse&json=1', '/karyotype?specie=3456yg&json=1']
chromo_length = ['/chromosomeLength?specie=&chromo=&json=1','/chromosomeLength?specie=human&chromo=3&json=1','/chromosomeLength?specie=human&chromo=ghb&json=1', '/chromosomeLength?specie=ghsdj&chromo=3&json=1']
# Medium level
gene_sequence = ['/geneSeq?gene=braf&json=1', '/geneSeq?gene=&json=1', '/geneSeq?gene=7415cz&json=1']
gene_info = ['/geneInfo?gene=frat2&json=1', '/geneInfo?gene=&json=1', '/geneInfo?gene=mnjk&json=1']
gene_calc = ['/geneCalc?gene=rvkem&json=1','/geneCalc?gene=frat1&json=1','/geneCalc?json=1&gene=']
gene_list = ['/geneList?chromo=2&start=0&end=300000&json=1','/geneList?start=0&end=300000&json=1']
print("\nConnecting to server: {}:{}\n".format(SERVER, PORT))


# Defining a function to connect to the server and get the json
def results(order):
    conn = http.client.HTTPConnection(SERVER, PORT)
    for i in order:
        conn.request("GET", i)
        # -- Read the response message from the server
        r1 = conn.getresponse()
        # -- Print the status line
        print("Response received!: {} {}\n".format(r1.status, r1.reason))
        # -- Read the response's body
        result = r1.read().decode("utf-8")
        print(result)


# Getting the results for each of the endpoints


print('Results for /listSpecies')
results(list_specie)

print('Results for /karyotype')
results(karyotype)

print('Results for /chromosomeLength')
results(chromo_length)

print('Results for /geneSeq')
results(gene_sequence)

print('Results for /geneInfo')
results(gene_info)

print('Results for /geneCalc')
results(gene_calc)

print('Results for /geneList')
results(gene_list)

