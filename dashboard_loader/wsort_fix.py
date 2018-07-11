from widget_def.models import *


fixings = [
    # Housing
    { 
        "urls": [ "rentalstress-housing-hero", "rentalstress-housing-hero-state", 
                    "housing_rentalstress", "housing_rentalstress_state" ],
        "new_sort_order": 1000
    },
    {
        "urls": [ "homelessness-housing-hero", "homelessness-housing-hero-state",
                    "housing_homelessness", "housing_homelessness_state" ],
        "new_sort_order": 1001
    },
    {
        "urls": [ "indigenous_homeownership-housing-hero", "indigenous_homeownership-housing-hero-state",
                    "housing_indigenous_homeownership", "housing_indigenous_homeownership_state" ],
        "new_sort_order": 1002
    },
    {
        "urls": [ "indigenous_overcrowding-housing-hero-state", "indigenous_overcrowding-housing-hero",
                    "housing_indigenous_overcrowding", "housing_indigenous_overcrowding_state"], 
        "new_sort_order": 1003
    },
    {
        "urls": [ "homelessness_npa-housing-hero", "homelessness_npa-housing-hero-state",
                    "housing_homelessness_npa", "housing_homelessness_npa_state"],
        "new_sort_order": 1010
    },
    {
        "urls": [ "housing_remote_overcrowding", "remote_overcrowding-housing-hero"],
        "new_sort_order": 1011
    },
    {
        "urls": [ "indigenous_remote-housing-hero", "indigenous_remote-housing-hero-state",
                    "housing_remote_indigenous", "housing_remote_indigenous_state"],
        "new_sort_order": 1012,
        "special_sort_order": {
            "match_view": "indigenous",
            "sort_order": 1510
        }
    },
    {
        "urls": [ "remote_condition-housing-hero", "housing_remote_condition"],
        "new_sort_order": 1013
    },

    # Education
    {
        "urls": [ "yr12-education-hero", "yr12-education-hero-state",
            "education_yr12", "education_yr12_state"],
        "new_sort_order": 1100
    },
    {
        "urls": [ "naplan_lit-education-hero", "naplan_lit-education-hero-state",
            "education_naplan_lit", "education_naplan_lit_state"],
        "new_sort_order": 1101
    },
    {
        "urls": [ "naplan_num-education-hero", "naplan_num-education-hero-state",
            "education_naplan_num", "education_naplan_num_state"],
        "new_sort_order": 1102
    },
    {
        "urls": [ "participation-education-hero", "participation-education-hero-state",
            "education_participation", "education_participation_state"],
        "new_sort_order": 1103
    },
    {
        "urls": [ "yr12_2015-education-hero", "yr12_2015-education-hero-state",
            "education_yr12_2015", "education_yr12_2015_state"],
        "new_sort_order": 1104
    },
    {
        "urls": [ "ecenqs-education-hero", "ecenqs-education-hero-state",
            "education_ecenqs", "education_ecenqs_state"],
        "new_sort_order": 1110
    },
    {
        "urls": [ "uaece-education-hero", "uaece-education-hero-state",
            "education_uaece", "education_uaece_state"],
        "new_sort_order": 1111
    },

    # Skills
    {
        "urls": ["cert3-skills-hero", "cert3-skills-hero-state",
                "skills_cert3", "skills_cert3_state"],
        "new_sort_order": 1200
    },
    {
        "urls": ["higher_qual-skills-hero", "higher_qual-skills-hero-state",
                "skills_higher_qual", "skills_higher_qual_state"],
        "new_sort_order": 1201
    },
    {
        "urls": ["improved_employ-skills-hero", "improved_employ-skills-hero-state",
                "skills_improved_employ", "skills_improved_employ_state"],
        "new_sort_order": 1202
    },
    {
        "urls": ["skills_reform-skills-hero", "skills_reform-skills-hero-state",
                "skills_reform", "skills_reform_state"],
        "new_sort_order": 1211
    },

    # Healthcare

    {
        "urls": ["life_expectancy-health-hero", "life_expectancy-health-hero-state",
                "health_life_expectancy", "health_life_expectancy_state"],
        "new_sort_order": 1300
    },
    {
        "urls": ["diabetes-health-hero", "diabetes-health-hero-state",
                "health_diabetes", "health_diabetes_state"],
        "new_sort_order": 1301
    },
    {
        "urls": ["healthyweight-health-hero", "healthyweight-health-hero-state",
                "health_healthyweight", "health_healthyweight_state"],
        "new_sort_order": 1302
    },
    {
        "urls": ["childweight-health-hero", "childweight-health-hero-state",
                "health_childweight", "health_childweight_state"],
        "new_sort_order": 1303
    },
    {
        "urls": ["smoking-health-hero", "smoking-health-hero-state",
                "health_smoking", "health_smoking_state"],
        "new_sort_order": 1304
    },
    {
        "urls": ["indig_smoking-health-hero", "indig_smoking-health-hero-state",
                "health_indig_smoking", "health_indig_smoking_state"],
        "new_sort_order": 1305
    },
    {
        "urls": ["edwait-health-hero", "edwait-health-hero-state",
                "health_edwait", "health_edwait_state"],
        "new_sort_order": 1306
    },
    {
        "urls": ["gpwait-health-hero", "gpwait-health-hero-state",
                "health_gpwait", "health_gpwait_state"],
        "new_sort_order": 1307
    },
    {
        "urls": ["avoidable-health-hero", "avoidable-health-hero-state",
                "health_avoidable", "health_avoidable_state"],
        "new_sort_order": 1308
    },
    {
        "urls": ["agedcare-health-hero", "agedcare-health-hero-state",
                "health_agedcare", "health_agedcare_state"],
        "new_sort_order": 1309
    },
    {
        "urls": ["mental-health-hero", "mental-health-hero-state",
                "health_mental", "health_mental_state"],
        "new_sort_order": 1310
    },

    # Disability

    {
        "urls": ["labour_participation-disability-hero", "labour_participation-disability-hero-state",
                "disability_labour_participation", "disability_labour_participation_state"],
        "new_sort_order": 1400
    },
    {
        "urls": ["more_assist-disability-hero", "more_assist-disability-hero-state",
                "disability_more_assist", "disability_more_assist_state"],
        "new_sort_order": 1401
    },
    {
        "urls": ["disability_social_participation", "disability_social_participation_state",
                "social_participation-disability-hero", "social_participation-disability-hero-state"],
        "new_sort_order": 1402
    },

    # Indigenous
    
    {
        "urls": [ "indig_mortality-indigenous-hero", "indig_mortality-indigenous-hero-state",
                    "indigenous_indig_mortality", "indigenous_indig_mortality_state", ],
        "new_sort_order": 1500
    },
    {
        "urls": [ "child_mortality-indigenous-hero", "child_mortality-indigenous-hero-state",
                    "indigenous_child_mortality", "indigenous_child_mortality_state", ],
        "new_sort_order": 1501
    },
    {
        "urls": [ "indig_ece-indigenous-hero", "indig_ece-indigenous-hero-state",
                    "indigenous_indig_ece", "indigenous_indig_ece_state", ],
        "new_sort_order": 1502
    },
    {
        "urls": [ "indig_lit-indigenous-hero", "indig_lit-indigenous-hero-state",
                    "indigenous_indig_lit", "indigenous_indig_lit_state", ],
        "new_sort_order": 1503
    },
    {
        "urls": [ "indig_num-indigenous-hero", "indig_num-indigenous-hero-state",
                    "indigenous_indig_num", "indigenous_indig_num_state", ],
        "new_sort_order": 1504
    },
    {
        "urls": [ "indig_yr12-indigenous-hero", "indig_yr12-indigenous-hero-state",
                    "indigenous_yr12", "indigenous_yr12_state", ],
        "new_sort_order": 1505
    },
    {
        "urls": [ "indig_employment-indigenous-hero", "indig_employment-indigenous-hero-state",
                    "indigenous_indig_employment", "indigenous_indig_employment_state", ],
        "new_sort_order": 1506
    },
    {
        "urls": [ "school_attendance-indigenous-hero", "school_attendance-indigenous-hero-state",
                    "indigenous_school_attendance", "indigenous_school_attendance_state", ],
        "new_sort_order": 1507
    },

    # Infrastructure

    {
        "urls": [ "projects-infrastructure-hero", "projects-infrastructure-hero-state",
                    "infrastructure_projects", "infrastructure_projects_state"],
        "new_sort_order": 1600
    },

    # Legal Assist

    {
        "urls": [ "legal_total_svc", "legal_total_svc_state",
                    "total_svc-legal-hero", "total_svc-legal-hero-state"],
        "new_sort_order": 1700
    }
]


for fix in fixings:
    print "Fix", repr(fix)
    rows = ViewWidgetDeclaration.objects.filter(definition__family__url__in=fix["urls"]).update(sort_order=fix["new_sort_order"])
    print "%d rows set to sort_order %d" % (rows, fix["new_sort_order"])
    if "special_sort_order" in fix:
        rows = ViewWidgetDeclaration.objects.filter(definition__family__url__in=fix["urls"], view__label__contains=fix["special_sort_order"]["match_view"]).update(sort_order=fix["special_sort_order"]["sort_order"])
        print "%d rows set to special sort_order %d" % (rows, fix["special_sort_order"]["sort_order"])
        
