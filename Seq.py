class Seq:
    strbases: object

    def __init__(self, strbases):
        print("Sequence {} created properly".format(strbases))
        self.strbases = strbases

    def len(self):
        tl = len(self.strbases)
        return tl

    def complement(self):
        compd = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G' }
        compseq = ''
        for i in self.strbases:
            compseq += compd[i]
        return compseq

    def reverse(self):
        reverted = self.strbases[::-1]
        return reverted

    def count(base):
        counter = 0
        for i in self.strbases:
            if i == base:
                counter += 1
        return counter

    def perc(self, base):
        tl = 0
        counter = 0
        for i in self.strbases:
            tl += 1
            if i == base:
                counter += 1
        if tl > 0:
            percentage = round(100.0 * counter / tl, 1)
            return percentage
        else:
            print("Can't calculate percentages with 0 length")
        return 0
