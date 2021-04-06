import argparse
import pytest
import unittest

from submodule_utils.arguments import *

class TestArguments(unittest.TestCase):
    def test_make_dict(self):
        subtypes_args = 'MMRD=0 P53ABN=1 P53WT=2 POLE=3'
        subtypes = make_dict(map(subtype_kv, subtypes_args.split(' ')))
        assert subtypes == {'MMRD':0, 'P53ABN': 1, 'P53WT': 2, 'POLE': 3}
    
    def test_make_dict_malformed(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            subtypes_args = 'MMRD=0 P53ABN=s P53WT=2 POLE=3'
            make_dict(map(subtype_kv, subtypes_args.split(' ')))
        
        with self.assertRaises(argparse.ArgumentTypeError):
            subtypes_args = 'MMRD=0 P53ABN=1 P53WT POLE=3'
            make_dict(map(subtype_kv, subtypes_args.split(' ')))
    
    def test_parse_balance_patches(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--balance_patches", type=balance_patches_options,
                required=False)
        args = parser.parse_args([])
        assert args.balance_patches == None
        args = parser.parse_args("--balance_patches group".split())
        assert args.balance_patches == 'group'
    
    def test_parse_subtype_kv(self):
        """Test that + nargs space separated words describing subtype=groupping pairs for a study are converted to a list of (key: str, value: int) pairs. 
        Example: if doing one-vs-rest on the subtypes MMRD vs P53ABN, P53WT and POLE then
        the input should be 'MMRD=0 P53ABN=1 P53WT=1 POLE=1'
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--subtypes", nargs='+', type=subtype_kv)
        args = parser.parse_args("--subtypes MMRd=0 p53abn=1 p53wt=2 POLE=3".split())
        assert args.subtypes == [('MMRD', 0), ('P53ABN', 1), ('P53WT', 2), ('POLE', 3)]

    def test_ParseKVToDictAction(self):
        """Test space separated words describing subtype=groupping pairs for a study
        Example: if doing one-vs-rest on the subtypes MMRD vs P53ABN, P53WT and POLE then
        the input should be 'MMRD=0 P53ABN=1 P53WT=1 POLE=1'
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--subtypes", nargs='+', type=subtype_kv,
                action=ParseKVToDictAction)
        args = parser.parse_args("--subtypes MMRd=0 p53abn=1 p53wt=2 POLE=3".split())
        assert args.subtypes == {'MMRD': 0, 'P53ABN': 1, 'P53WT': 2, 'POLE': 3}
    
    def test_many_ParseKVToDictAction(self):
        default_subtypes = {'MMRD': 0, 'P53ABN': 1, 'P53WT': 2, 'POLE': 3}
        parser = argparse.ArgumentParser()
        parser.add_argument("--subtypes", nargs='+', type=subtype_kv,
                action=ParseKVToDictAction, default=default_subtypes)
        args = parser.parse_args([])
        assert args.subtypes == default_subtypes
        args = parser.parse_args("--subtypes IDHWT=0 IDHNC=1 IDHC=2".split())
        assert args.subtypes == {'IDHWT': 0, 'IDHNC': 1, 'IDHC': 2}
        args = parser.parse_args("--subtypes cholesterogenic=0 glycolytic=1 mixed=2 quiescent=3".split())
        assert args.subtypes == {'CHOLESTEROGENIC': 0, 'GLYCOLYTIC': 1,
                'MIXED': 2, 'QUIESCENT': 3}
        
    def test_parse_str_kv(self):
        default_filter_labels = {}
        parser = argparse.ArgumentParser()
        parser.add_argument("--filter_labels", nargs='+', type=str_kv,
                action=ParseKVToDictAction, default=default_filter_labels)
        args = parser.parse_args([])
        assert args.filter_labels == default_filter_labels
        args = parser.parse_args("--filter_labels annotation=Tumor".split())
        assert args.filter_labels == {"annotation": "Tumor"}
        args = parser.parse_args("--filter_labels annotation=Tumor patch_size=256 magnification=10".split())
        assert args.filter_labels == {"annotation": "Tumor", "patch_size": "256",
                "magnification": "10"}
