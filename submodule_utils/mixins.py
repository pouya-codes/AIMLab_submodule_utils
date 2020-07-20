class OutputMixin(object):
    '''Mixin gives a runner class methods to print LaTeX and Markdown figures

    Attributes
    ----------
    CategoryEnum : enum.Enum
        The enum representing the categories and is one of (SubtypeEnum, BinaryEnum)
    '''

    def latex_formatter(self, counts, prefix):
        '''Prints LaTeX row with counts to STDOUT

        Parameters
        ----------
        counts : ndarray
            The counts to fill each cell

        prefix : str
            The name of the latex row to print
        '''
        prefix = prefix.replace('_', ' ')
        output = r'{}'.format(prefix)
        for count in counts:
            output += r' & \num[group-separator={{,}}]{{{}}}'.format(int(count))
        output += r' & \num[group-separator={{,}}]{{{}}} \\'.format(int(counts.sum()))
        output += '\n'
        return output

    def markdown_formatter(self, counts, prefix):
        '''Prints Markdown row with counts to STDOUT

        Parameters
        ----------
        counts : ndarray
            The counts to fill each cell

        prefix : str
            The name of the Markdown row to print
        '''
        prefix = prefix.replace('_', ' ')
        output = '| {} |'.format(prefix)
        for count in counts:
            output += ' {} |'.format(int(count))
        output += ' {} |\n'.format(int(counts.sum()))
        return output

    def markdown_header(self, heading):
        '''Prints Markdown header row to STDOUT

        Parameters
        ----------
        heading : string
            The name of the table this header is part of
        '''
        output = f'|| {heading} ||'
        for s in self.CategoryEnum:
            output += ' {} ||'.format(s.name)
        output += ' Total ||\n'
        return output