import importlib.util, pathlib, unittest
P=pathlib.Path(__file__).resolve().parents[1]/"scripts"/"output_naming.py"
spec=importlib.util.spec_from_file_location("naming",P); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class T(unittest.TestCase):
    def test_eurasia(self): self.assertEqual(m.build_name("PassiveDefense","Proposal","Eurasia"),"HRT_PassiveDefense_Proposal_Eurasia.docx")
    def test_scope(self): self.assertEqual(m.build_name("PassiveDefense","Proposal","Eurasia","Chapter01"),"HRT_PassiveDefense_Proposal_Eurasia_Chapter01.docx")
    def test_revision(self): self.assertEqual(m.build_name("FS","Report","Project X",revision="R01"),"HRT_FS_Report_Project_X_R01.docx")
    def test_user_filename(self): self.assertEqual(m.build_name("X","Y","Z",user_filename="My Report.docx"),"My_Report.docx")
if __name__=="__main__": unittest.main()
