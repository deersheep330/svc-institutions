from institutions.parser import InstitutionsOverboughtParser, InstitutionsOversoldParser

if __name__ == '__main__':

    overbought_parser = InstitutionsOverboughtParser()
    overbought_parser.parse()

    oversold_parser = InstitutionsOversoldParser()
    oversold_parser.parse()