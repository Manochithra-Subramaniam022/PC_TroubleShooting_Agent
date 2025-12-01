import streamlit as st
import json

# --- Core Logic (from your troubleshooter.py) ---

def load_knowledge_base(file_path):
    """Loads the knowledge base from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def find_matching_rule(facts, rules):
    """Finds a rule that matches the current set of facts."""
    for rule in rules:
        if all(condition in facts for condition in rule['if']):
            if rule['then'] not in facts:
                return rule
    return None

# --- Streamlit App ---

# Load knowledge base once
kb = load_knowledge_base('knowledge_base.json')
rules = kb['rules']
questions = kb['questions']
suggestions = kb['suggestions']

# App title
st.title("PC Troubleshooting Agent 🤖")

# Initialize session state to store facts
if 'facts' not in st.session_state:
    st.session_state.facts = []
if 'step' not in st.session_state:
    st.session_state.step = "initial_problem"
if 'conclusion' not in st.session_state:
    st.session_state.conclusion = None

# --- UI Logic ---

# Step 1: Ask for the initial problem
if st.session_state.step == "initial_problem":
    st.write("Please choose the problem you are facing:")
    
    # Create a button for each initial problem
    for key, value in kb['initial_problems'].items():
        if st.button(value.replace('_', ' ').title()):
            st.session_state.facts = [value]
            st.session_state.step = "diagnosing"
            st.rerun() # Rerun the script to move to the next step

# Step 2: The main diagnosis loop
elif st.session_state.step == "diagnosing":
    rule = find_matching_rule(st.session_state.facts, rules)
    
    if rule:
        st.session_state.conclusion = rule['then']
        
        # If the conclusion is a question
        if st.session_state.conclusion.startswith('ask_'):
            question_text = questions[st.session_state.conclusion]
            st.write(f"❓ {question_text}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes"):
                    # FIX WAS HERE
                    new_fact = f"{st.session_state.conclusion.replace('ask_', '')}_yes"
                    st.session_state.facts.append(st.session_state.conclusion)
                    st.session_state.facts.append(new_fact)
                    st.rerun()
            with col2:
                if st.button("No"):
                    # AND FIX WAS HERE
                    new_fact = f"{st.session_state.conclusion.replace('ask_', '')}_no"
                    st.session_state.facts.append(st.session_state.conclusion)
                    st.session_state.facts.append(new_fact)
                    st.rerun()

        # If the conclusion is a final suggestion
        elif st.session_state.conclusion.startswith('suggestion_'):
            st.session_state.step = "finished"
            st.rerun()

    else: # No more rules match
        st.error("Sorry, I could not determine the cause of the problem based on the information provided. 😥")

# Step 3: Show the final result
elif st.session_state.step == "finished":
    suggestion_text = suggestions[st.session_state.conclusion]
    st.success(f"Diagnosis Complete: {suggestion_text} ✅")
    st.balloons()
    
    if st.button("Start Over"):
        # Reset session state to start again
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()