from psy_test.models import *

def erase_db():
    if PsyTest.objects.all().count() > 0:
        print("Cancello il DB")
        PsyTest.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        TestResult.objects.all().delete()

def init_db():
    list_tests = [
        ("Test sul PTSD",
         "Il test per valutare l'eventuale presenza di un trauma da stress che puoi svolgere qui è il PCL-5 (Posttraumatic Stress Disorder Checklist), uno strumento di screening riconosciuto dalla comunità scientifica internazionale.",
         "test-sul-ptsd"
        ),
        ("Test sui DCA",
         "Il test sui disturbi alimentari che puoi svolgere qui è l’EAT-26 (Eating Attitude Test), uno strumento di screening riconosciuto dalla comunità scientifica internazionale.", 
         "test-sui-dca" 
        ),
    ]

    lista_questions_PTSD = [
        "Ricordi ripetuti, disturbanti e indesiderati dell'esperienza stressante che hai subito?",
        "Sogni ricorrenti e disturbanti dell'esperienza stressante?",
        "Avere la sensazione o comportarsi improvvisamente come se l'esperienza stressante si stesse verificando nuovamente (come se si rivivessi la stessa esperienza)?", 
    ]

    list_answers = [
        {"A": "Per niente"}, 
        {"B": "Poco"}, 
        {"C": "Moderatamente"}, 
        {"D": "Molto"}, 
        {"E": "Moltissimo"},    
    ]

    for t in list_tests:
        t_db = PsyTest()
        t_db.title = t[0]
        t_db.description = t[1]
        t_db.slug = t[2]
        t_db.save()
        if "PTSD" in t[0]:
            for q in lista_questions_PTSD:
                q_db = Question()
                q_db.rel_test = t_db
                q_db.question = q
                q_db.save()
                for a_dict in list_answers: 
                    a_db = Answer()
                    a_db.rel_question = q_db
                    a_db.answer_type = list(a_dict.keys())[0]
                    a_db.answer = a_dict[a_db.answer_type]

                    a_db.save()
        

    tests = PsyTest.objects.all()

    for _, test in enumerate(tests):
        for ans in list_answers: 
            ind_db = TestResult()
            ind_db.rel_test = test
            for akey, aval in ans.items():
                ind_db.title = aval
                ind_db.answer_type = akey
                ind_db.content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
            ind_db.save()


    # print("DUMP DB")
    # print("PsyTest")
    # for t in tests:
    #     print(t)
    # print("Test Results")
    # for tr in TestResult.objects.all():
    #     print(tr)        



