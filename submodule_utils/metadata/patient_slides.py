import json
import itertools

class PatientSlidesMetadata(object):
    """Represents patient slides manifest.

    PatientSlidesMetadata saves/load a patient slides JSON file with this format.

    ```
    PATIENT_REGEX := string of regex to search patient ID from slide ID | null
    PATH := list of string of slide path
    LABELS := list of string of slide level label | null
    {
        patient_regex: [[ PATIENT_REGEX ]],
        patients: {
            [[patient ID]]:  {
                slides: [
                    {
                        path: [[ PATH ]],
                        labels: [[ LABELS ]],
                        [[key]]: [[value]],
                        ...
                    },
                    ...
                ],
            },
            ...
        }
    }
    ```
    """
    @classmethod
    def load(cls, patient_slides_file):
        """Load slide_coords from JSON file at patient_slides_file
        """
        patient_slides = cls(patient_slides_file)
        patient_slides.store = json.loads(patient_slides.patient_slides_file)
        patient_slides.load_patient_slides()
        return patient_slides
    
    def __init__(self, patient_slides_file,
            patient_regex="^[A-Z]*-?(\d*).*\(?.*\)?.*$"):
        self.patient_slides_file = patient_slides_file
        self.store = { 'patients': { }, 'patient_regex': patient_regex }
    
    @property
    def patients(self):
        """Get all patients.
        """
        return self.store['patients']
    
    @property
    def slidepaths(self):
        """Get all slide paths across all patients.
        """
        return list(itertools.chain.from_iterable(self.patients.values()))
    
    def add_to_patient(self, patient_id, *slidepaths):
        if patient_id not in self.store['patients']:
            self.store['patients'][patient_id] = [ ]
        self.store['patients'][patient_id].extend(slidepaths)
    
    def save(self):
        with open(self.patient_slides_file, 'w') as f:
            json.dump(self.store, f)