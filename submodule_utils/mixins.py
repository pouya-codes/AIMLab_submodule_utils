from tabulate import tabulate
import pandas as pd

import submodule_utils as utils

class OutputMixin(object):
    """Mixin gives a runner class methods to generate data frame tables tabulating patches in datasets, and prints LaTeX and Markdown figures.
    
    When using the methods of this mixin, please make sure the attributes of this mixin is present in the inheriting class.

    Attributes
    ----------
    is_binary : bool

    patch_pattern : dict of (str: int)

    CategoryEnum : enum.Enum
        The enum representing the categories and is one of (SubtypeEnum, BinaryEnum)
    
    dataset_origin : str
        Dataset origin used to extract patient name from slide name.
    """

    def latex_formatter(self, counts, prefix):
        """Prints LaTeX row with counts to STDOUT

        Parameters
        ----------
        counts : ndarray
            The counts to fill each cell

        prefix : str
            The name of the latex row to print
        """
        prefix = prefix.replace('_', ' ')
        output = r'{}'.format(prefix)
        for count in counts:
            output += r' & \num[group-separator={{,}}]{{{}}}'.format(int(count))
        output += r' & \num[group-separator={{,}}]{{{}}} \\'.format(int(counts.sum()))
        output += '\n'
        return output

    def markdown_formatter(self, counts, prefix):
        """Prints Markdown row with counts to STDOUT

        Parameters
        ----------
        counts : ndarray
            The counts to fill each cell

        prefix : str
            The name of the Markdown row to print
        """
        prefix = prefix.replace('_', ' ')
        output = '| {} |'.format(prefix)
        for count in counts:
            output += ' {} |'.format(int(count))
        output += ' {} |\n'.format(int(counts.sum()))
        return output

    def markdown_header(self, heading):
        """Prints Markdown header row to STDOUT

        Parameters
        ----------
        heading : string
            The name of the table this header is part of
        """
        output = f'|| {heading} ||'
        for s in self.CategoryEnum:
            output += ' {} ||'.format(s.name)
        output += ' Total ||\n'
        return output

    def generate_total_summary_table(self, groups, table_name=None, group_names=None):
        """Generate a summary table tabulating group level information from the parsed group file.
        Counts the same patch under different patch size and magnification as different patches.

        Parameters
        ----------
        groups : dict
            Groups in Mitch format
        
        group_names : dict
            Lookup for group name from group index to use in summary table row.

        Returns
        -------
        dict of (str: pandas.DataFrame)
            The dictionary of the summary tables in data frame. Contains:
             - slide_patches
             - patient_patches
             - patient_slides
             - total_patches
             - total_slides
             - total_patients
        
        TODO: not tested yet
        """
        groups['chunks'].sort(key=lambda chunk: chunk['id'])

        patch_paths = []
        for chunk in groups['chunks']:
            patch_paths.extend(chunk['imgs'])
            
        category_names = [c.name for c in self.CategoryEnum]
        patches = {name: set() for name in category_names}
        slides = {name: set() for name in category_names}
        patients = {name: set() for name in category_names}
        all_patches = set()
        all_slides = set()
        all_patients = set()
        cum_header = 'Overall' if self.is_binary else 'Total'
        headers = category_names + [cum_header]
        num_headers = len(headers)
        total_patches = pd.DataFrame(columns=headers)
        total_slides = pd.DataFrame(columns=headers)
        total_patients = pd.DataFrame(columns=headers)
        patient_patches = pd.DataFrame(columns=headers)
        slide_patches = pd.DataFrame(columns=headers)
        patient_slides = pd.DataFrame(columns=headers)
        for patch_path in patch_paths:
            patch_id = utils.create_patch_id(patch_path, self.patch_pattern)
            label = utils.get_label_by_patch_id(patch_id, self.patch_pattern,
                    self.CategoryEnum, is_binary=self.is_binary).name
            slide_name = utils.get_slide_by_patch_id(patch_id, self.patch_pattern)
            patient_id = utils.get_patient_by_slide_id(slide_name,
                    dataset_origin=self.dataset_origin)

            patches[label].add(patch_id)

            if slide_name not in slides[label]:
                if patient_id not in patient_slides.index:
                    patient_slides.loc[patient_id] = [0] * num_headers
                patient_slides.at[patient_id, label] += 1
                if slide_name not in all_slides:
                    patient_slides.at[patient_id, cum_header] += 1
                
            slides[label].add(slide_name)
            patients[label].add(patient_id)

            if patient_id not in patient_patches.index:
                patient_patches.loc[patient_id] = [0] * num_headers
            patient_patches.at[patient_id, label] += 1
            if patient_id not in all_patients:
                patient_patches.at[patient_id, cum_header] += 1

            if slide_name not in slide_patches.index:
                slide_patches.loc[slide_name] = [0] * num_headers
            slide_patches.at[slide_name, label] += 1
            if slide_name not in all_slides:
                slide_patches.at[slide_name, cum_header] += 1

            all_patches.add(patch_id)
            all_slides.add(slide_name)
            all_patients.add(patient_id)
        
        for label, s in patches.items():
            total_patches['Total', label] = len(s)
        total_patches['Total', cum_header] = len(all_patches)
        for label, s in slides.items():
            total_slides['Total', label] = len(s)
        total_slides['Total', cum_header] = len(all_slides)
        for label, s in patients.items():
            total_patients['Total', label] = len(s)
        total_patients['Total', cum_header] = len(all_patients)

        patient_patches.loc["Total"] = patient_patches.sum().astype(int)
        slide_patches.loc["Total"] = slide_patches.sum().astype(int)
        patient_slides.loc["Total"] = patient_slides.sum().astype(int)

        return {
            'slide_patches': slide_patches,
            'patient_patches': patient_patches,
            'patient_slides': patient_slides,
            'total_patches': total_patches,
            'total_slides': total_slides,
            'total_patients': total_patients,
        }


    def generate_group_summary_table(self, groups, group_names=None):
        """Generate a summary table tabulating group level information from the parsed group file.
        Counts the same patch under different patch size and magnification as different patches.

        Parameters
        ----------
        groups : dict
            Groups in Mitch format
        
        group_names : dict of (int: str)
            Lookup for group name from group index to use in summary table row.

        Returns
        -------
        dict of (str: pandas.DataFrame)
            The dictionary of the summary tables in data frame. Contains:
             - group_patches
             - group_slides
             - group_patients
             - patient_patches
             - slide_patches
             - patient_slides
        """
        output = {
            'patient_patches': {},
            'slide_patches': {},
            'patient_slides': {},
        }
        groups['chunks'].sort(key=lambda chunk: chunk['id'])
        category_names = sorted([c.name for c in self.CategoryEnum])
        cum_header = 'Overall' if self.is_binary else 'Total'
        headers = category_names + [cum_header]
        num_headers = len(headers)
        group_patches = pd.DataFrame(columns=headers)
        group_slides = pd.DataFrame(columns=headers)
        group_patients = pd.DataFrame(columns=headers)
        for chunk in groups['chunks']:
            try:
                group_name = group_names[chunk['id']]
            except (TypeError, KeyError):
                group_name = f"Group {chunk['id'] + 1}"
            patch_paths = chunk['imgs']
            patches = {name: set() for name in category_names}
            slides = {name: set() for name in category_names}
            patients = {name: set() for name in category_names}
            all_patches = set()
            all_slides = set()
            all_patients = set()
            patient_patches = pd.DataFrame(columns=headers)
            slide_patches = pd.DataFrame(columns=headers)
            patient_slides = pd.DataFrame(columns=headers)
            for patch_path in patch_paths:
                patch_id = utils.create_patch_id(patch_path, self.patch_pattern)
                label = utils.get_label_by_patch_id(patch_id, self.patch_pattern,
                        self.CategoryEnum, is_binary=self.is_binary).name
                slide_name = utils.get_slide_by_patch_id(patch_id, self.patch_pattern)
                patient_id = utils.get_patient_by_slide_id(slide_name,
                        dataset_origin=self.dataset_origin)

                patches[label].add(patch_id)

                if slide_name not in slides[label]:
                    if patient_id not in patient_slides.index:
                        patient_slides.loc[patient_id] = [0] * num_headers
                    patient_slides.at[patient_id, label] += 1
                    if slide_name not in all_slides:
                        patient_slides.at[patient_id, cum_header] += 1
                 
                slides[label].add(slide_name)
                patients[label].add(patient_id)

                if patient_id not in patient_patches.index:
                    patient_patches.loc[patient_id] = [0] * num_headers
                patient_patches.at[patient_id, label] += 1
                patient_patches.at[patient_id, cum_header] += 1

                if slide_name not in slide_patches.index:
                    slide_patches.loc[slide_name] = [0] * num_headers
                slide_patches.at[slide_name, label] += 1
                slide_patches.at[slide_name, cum_header] += 1

                all_patches.add(patch_id)
                all_slides.add(slide_name)
                all_patients.add(patient_id)

            for label, s in patches.items():
                group_patches.at[group_name, label] = len(s)
            group_patches.at[group_name, cum_header] = len(all_patches)
            for label, s in slides.items():
                group_slides.at[group_name, label] = len(s)
            group_slides.at[group_name, cum_header] = len(all_slides)
            for label, s in patients.items():
                group_patients.at[group_name, label] = len(s)
            group_patients.at[group_name, cum_header] = len(all_patients)

            patient_patches.loc["Total"] = patient_patches.sum().astype(int)
            slide_patches.loc["Total"] = slide_patches.sum().astype(int)
            patient_slides.loc["Total"] = patient_slides.sum().astype(int)
            output['patient_patches'][group_name] = patient_patches
            output['slide_patches'][group_name] = slide_patches
            output['patient_slides'][group_name] = patient_slides
        
        group_patches.loc['Total'] = group_patches.sum().astype(int)
        group_slides.loc['Total'] = group_slides.sum().astype(int)
        group_patients.loc['Total'] = group_patients.sum().astype(int)
        output['group_patches'] = group_patches
        output['group_slides'] = group_slides
        output['group_patients'] = group_patients
        return output
    
    def print_group_summary(self, groups, group_names=None, detailed=False, tablefmt='jira'):
        """Prints summary table tabulating group level information from the parsed group file as JIRA tables.

        Parameters
        ----------
        groups : dict
            Groups in Mitch format
        
        group_names : dict of (int: str)
            Lookup for group name from group index to use in summary table row.
        
        detailed : boolean
            True to print detailed patch and slide count breakdown for each slide and patient in the groups.
        
        tablefmt : str
            Table type passed to tabulate method to format table. Defaults to JIRA table formatting.

        Returns
        -------
        dict
            The same output as OutputMixin.generate_group_summary_table
        """
        output = self.generate_group_summary_table(groups, group_names)

        """Group patches table"""
        group_patches = output['group_patches']
        headers = ["Group Patches",] + group_patches.columns.tolist()
        print()
        print(tabulate(group_patches, headers=headers, tablefmt=tablefmt))
        print()

        """Group slides table"""
        group_slides = output['group_slides']
        headers = ["Group Slides",] + group_slides.columns.tolist()
        print()
        print(tabulate(group_slides, headers=headers, tablefmt=tablefmt))
        print()

        """Group patients table"""
        group_patients = output['group_patients']
        headers = ["Group Patients",] + group_patients.columns.tolist()
        print()
        print(tabulate(group_patients, headers=headers, tablefmt=tablefmt))
        print()

        if detailed:
            print("Patient Patches")
            for group_name, tally in output['patient_patches'].items():
                headers = [group_name,] + tally.columns.tolist()
                print()
                print(tabulate(tally, headers=headers, tablefmt=tablefmt))
                print()
            
            print("Patient Slides")
            for group_name, tally in output['patient_slides'].items():
                headers = [group_name,] + tally.columns.tolist()
                print()
                print(tabulate(tally, headers=headers, tablefmt=tablefmt))
                print()
            
            print("Slide Patches")
            for group_name, tally in output['slide_patches'].items():
                headers = [group_name,] + tally.columns.tolist()
                print()
                print(tabulate(tally, headers=headers, tablefmt=tablefmt))
                print()
        return output
