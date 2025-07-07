import requests
import re
import openai
import os

class Summarizer:
    '''
    Summarizer Class. Contains methods to summarize area forecast discussions and also explain selected sections of text from 
    the summarized forecast discussions that the user does not understand. 

    Need to add a method to summarize region wide tropical weather discussions
    Need to add a method to summarize storm specific discussions

    '''
    def __init__(self, weather_knowledge, afd = None, twd_discussion = None, storm_discussion = None):
        '''
        Summarizer object initialization method (constructor)

        @param weather_knowledge the users weather expertise - controls the level at which the afd is summarized. Will either be 
            "expert", "moderate", "none", or "no_summary". Also controls the level at which text explanations are explained.
        @param afd the area forecast discussion that will be summarized
        @param twd_discussion the tropical weather discussion pulled from the nhc
        @param storm_discussion the specifc discussion related to a tropical storm. 
        '''
        self.weather_knowledge = weather_knowledge
        self.afd = afd
        self.twd_discussion = twd_discussion
        self.storm_discussion = storm_discussion

    def generate_Message(self):
        '''
        Builds the prompt string and passes it to openai, currently using the gpt-4.1-mini model to summarize the text.
        Prompt string is build based on the weather_knowledge

        @return the summarized text string
        '''
        if self.weather_knowledge == "expert":
            prompt_string = """You are a meteorologist and educator. Your task is to write a clear, structured weather summary for a general audience based on the latest NWS Area Forecast Discussion (AFD). Your summary should explain what the weather will be and what is causing it, with a focus on today, tonight, and tomorrow. You may briefly mention days 2-4 only if significant weather is forecast. 
                                
                                Write for this specific audience level: Expert – For those with a meteorology background. Use technical terms (e.g., CAPE, shear, shortwaves, synoptic features) and concise scientific explanations. Keep it focused and professional.

                                Each version should be 1-2 concise paragraphs.
                                Always explain key features driving the weather (e.g., fronts, upper-level disturbances, instability, etc.).
                                Do not copy and paste from the AFD—synthesize and explain.
                                Avoid long lists of temperatures or chance-of-rain percentages.
                                Do not make any information up, everything you output must be pulled from the provided forecast discussion
                                Maintain a consistent tone and structure.

                                The AFD will be entered into the chat\n"""
            
            afd = """You are a meteorologist and educator. Your task is to write a clear, structured weather summary for a general audience based on the latest NWS Area Forecast Discussion (AFD). Your summary should explain what the weather will be and what is causing it, with a focus on today, tonight, and tomorrow. You may briefly mention days 2-4 only if significant weather is forecast. 
                                
                                Write for this specific audience level: Expert – For those with a meteorology background. Use technical terms (e.g., CAPE, shear, shortwaves, synoptic features) and concise scientific explanations. Keep it focused and professional.

                                Each version should be 1-2 concise paragraphs.
                                Always explain key features driving the weather (e.g., fronts, upper-level disturbances, instability, etc.).
                                Do not copy and paste from the AFD—synthesize and explain.
                                Avoid long lists of temperatures or chance-of-rain percentages.
                                Do not make any information up, everything you output must be pulled from the provided forecast discussion
                                Maintain a consistent tone and structure.

                                The area forecast discussion is as follows\n"""
            
        elif self.weather_knowledge == "moderate":
            prompt_string = """You are a meteorologist and educator. Your task is to write a clear, structured weather summary for a general audience based on the latest NWS Area Forecast Discussion (AFD). Your summary should explain what the weather will be and what is causing it, with a focus on today, tonight, and tomorrow. You may briefly mention days 2-4 only if significant weather is forecast. 
                                
                                Write for this specific audience level: Moderate – For weather enthusiasts or TV-weather-savvy readers. Use plain language with light explanations of weather features (e.g., “a weak front will bring…”). Include some causes and effects without overwhelming detail.

                                Each version should be 1-2 concise paragraphs.
                                Always explain key features driving the weather (limit jargon to cold fronts, warm fronts, high, and low pressure systems).
                                Do not copy and paste from the AFD—synthesize and explain, but you may use it.
                                Avoid long lists of temperatures or chance-of-rain percentages.
                                Do not make any information up, everything you output must be pulled from the provided forecast discussion
                                Maintain a consistent tone and structure.

                                The AFD will be entered into the chat\n"""
            
            afd = """You are a meteorologist and educator. Your task is to write a clear, structured weather summary for a general audience based on the latest NWS Area Forecast Discussion (AFD). Your summary should explain what the weather will be and what is causing it, with a focus on today, tonight, and tomorrow. You may briefly mention days 2-4 only if significant weather is forecast. 
                                
                                Write for this specific audience level: Moderate – For weather enthusiasts or TV-weather-savvy readers. Use plain language with light explanations of weather features (e.g., “a weak front will bring…”). Include some causes and effects without overwhelming detail.

                                Each version should be 1-2 concise paragraphs.
                                Attempt explain key features driving the weather (limit jargon to cold fronts, warm fronts, high, and low pressure systems).
                                Do not copy and paste from the AFD—synthesize and explain, but you may use it.
                                Avoid long lists of temperatures or chance-of-rain percentages.
                                Do not make any information up, everything you output must be pulled from the provided forecast discussion
                                Maintain a consistent tone and structure.

                                The area forecast discussion is as follows\n"""
            
        elif self.weather_knowledge == "none":
            prompt_string = """You are a meteorologist and educator. Your task is to write a clear, structured weather summary for a general audience based on the latest NWS Area Forecast Discussion (AFD). Your summary should explain what the weather will be and what is causing it, with a focus on today, tonight, and tomorrow. You may briefly mention days 2-4 only if significant weather is forecast. 
                                
                                Write for this specific audience level: For the general public. Use simple, clear language with basic educational value. Focus on what will happen and why, without jargon. Be respectful and informative without sounding condescending.

                                Each version should be 1-2 concise paragraphs.
                                Attempt to explain key features driving the weather without the use of jargon such fronts, upper-level disturbances, etc.).
                                Do not copy and paste from the AFD—synthesize and explain, but you may use it.
                                Avoid long lists of temperatures or chance-of-rain percentages.
                                Do not make any information up, everything you output must be pulled from the provided forecast discussion
                                Maintain a consistent tone and structure.

                                The AFD will be entered into the chat\n"""
            
            afd = """You are a meteorologist and educator. Your task is to write a clear, structured weather summary for a general audience based on the latest NWS Area Forecast Discussion (AFD). Your summary should explain what the weather will be and what is causing it, with a focus on today, tonight, and tomorrow. You may briefly mention days 2-4 only if significant weather is forecast. 
                                
                                Write for this specific audience level: For the general public. Use simple, clear language with basic educational value. Focus on what will happen and why, without jargon. Be respectful and informative without sounding condescending.

                                Each version should be 1-2 concise paragraphs.
                                Attempt to explain key features driving the weather without the use of jargon, limit jargon to cold fronts, warm fronts, high, and low pressure systems).
                                Do not copy and paste from the AFD—synthesize and explain.
                                Avoid long lists of temperatures or chance-of-rain percentages.
                                Do not make any information up, everything you output must be pulled from the provided forecast discussion
                                Maintain a consistent tone and structure.

                                The area forecast discussion is as follows\n"""
        elif self.weather_knowledge == "no_summary":
            afd = ""

        afd += "\n" + self.afd

        # no need to talk to openai if the user does not want a summary. 
        if self.weather_knowledge == "no_summary":
            text = afd
            text = clean_no_summary_text(text)
        else:
            # connect to openai
            openai.api_key = os.getenv("API_KEY") 

            # build messages data structure to pass to openai
            messages = [
                {"role": "system", "content": prompt_string},
                {"role": "user", "content": afd}
            ]
            try:
                # create chat message
                response = openai.chat.completions.create(
                    model="gpt-4.1-mini", 
                    messages=messages,
                    temperature=0.7
                )
                # get response
                text = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API Error: {e}")
                text = "There was an error generating the summary."
        
        return text
    
    def explain_text(self, selected_text, summary):
        '''
        Passes the selected text along with the summary and the original afd to explain the selected text. Currently using the gpt-4.1-mini model for explanations.
        Prompt determined by the objects weather_knowledge

        @param selected_text the selected portion of the summarized text from the webpage, this is the section of text that is supposed to explain the section
        @param summary the summarized forecast discussion, this is important for context
        @return text the explanation generated by the llm. 
        '''
        if self.weather_knowledge == "expert":
            prompt_string = """You are a meteorologist and educator. user is reading a summarized weather forecast that was generated from an official National Weather Service Area Forecast Discussion (AFD) or NHC Tropical Weather Discussion/Storm Specific Discussion. 
                                Your job is to clearly explain what that selected text means, using context from both the original discussion and the summary.

                                Write for this specific audience level: Expert – For those with a meteorology background. Use technical terms (e.g., CAPE, shear, shortwaves, synoptic features), but if these terms are the focus of
                                of the selected text the user may need you to explain them as well.

                                An explanation should be concise.
                                Do not make any information up.
                                Maintain a consistent tone and structure as seen in the summary.

                                Only explain the selected phrase in context — don’t summarize the whole forecast.
                                
                                The original discussion and summary will be entered in the chat, make sure to use them to gain context for the selected section. \n"""
            
            afd = """You are a meteorologist and educator. user is reading a summarized weather forecast that was generated from an official National Weather Service Area Forecast Discussion (AFD) or NHC Tropical Weather Discussion/Storm Specific Discussion. 
                                Your job is to clearly explain what that selected text means, using context from both the original discussion and the summary.

                                Write for this specific audience level: Expert – For those with a meteorology background. Use technical terms (e.g., CAPE, shear, shortwaves, synoptic features), but if these terms are the focus of
                                of the selected text the user may need you to explain them as well.

                                An explanation should be concise.
                                Do not make any information up.
                                Maintain a consistent tone and structure as seen in the summary.

                                Only explain the selected phrase in context — don’t summarize the whole forecast.
                                
                                The original discussion and summary will be entered in the chat, make sure to use them to gain context for the selected section. \n"""
            
        elif self.weather_knowledge == "moderate":
            prompt_string = """You are a meteorologist and educator. user is reading a summarized weather forecast that was generated from an official National Weather Service Area Forecast Discussion (AFD) or NHC Tropical Weather Discussion/Storm Specific Discussion. 
                                Your job is to clearly explain what that selected text means, using context from both the original discussion and the summary.
                      
                                Write for this specific audience level: Moderate – For weather enthusiasts or TV-weather-savvy readers. Use plain language with light explanations of weather features (e.g., “a weak front will bring…”). Include some causes and effects without overwhelming detail. If these terms are the focus of
                                of the selected text the user may need you to explain them as well.

                                An explanation should be concise.
                                Do not make any information up.
                                Maintain a consistent tone and structure as seen in the summary.

                                Only explain the selected phrase in context — don’t summarize the whole forecast.
                                
                                The original discussion and summary will be entered in the chat, make sure to use them to gain context for the selected section. \n"""
            
            afd = """You are a meteorologist and educator. user is reading a summarized weather forecast that was generated from an official National Weather Service Area Forecast Discussion (AFD) or NHC Tropical Weather Discussion/Storm Specific Discussion. 
                                Your job is to clearly explain what that selected text means, using context from both the original discussion and the summary.
                      
                                Write for this specific audience level: Moderate – For weather enthusiasts or TV-weather-savvy readers. Use plain language with light explanations of weather features (e.g., “a weak front will bring…”). Include some causes and effects without overwhelming detail. If these terms are the focus of
                                of the selected text the user may need you to explain them as well.

                                An explanation should be concise.
                                Do not make any information up.
                                Maintain a consistent tone and structure as seen in the summary.

                                Only explain the selected phrase in context — don’t summarize the whole forecast.
                                
                                The original discussion and summary will be entered in the chat, make sure to use them to gain context for the selected section. \n"""
            
        elif self.weather_knowledge == "none":
            prompt_string = """You are a meteorologist and educator. user is reading a summarized weather forecast that was generated from an official National Weather Service Area Forecast Discussion (AFD) or NHC Tropical Weather Discussion/Storm Specific Discussion. 
                                Your job is to clearly explain what that selected text means, using context from both the original discussion and the summary.
                             
                                Write for this specific audience level: For the general public. Use simple, clear language with basic educational value. Focus on what will happen and why, without jargon. Be respectful and informative without sounding condescending.

                                An explanation should be concise.
                                Do not make any information up.
                                Maintain a consistent tone and structure as seen in the summary.

                                Only explain the selected phrase in context — don’t summarize the whole forecast.
                                
                                The original discussion and summary will be entered in the chat, make sure to use them to gain context for the selected section. \n"""
            
            afd = """You are a meteorologist and educator. user is reading a summarized weather forecast that was generated from an official National Weather Service Area Forecast Discussion (AFD) or NHC Tropical Weather Discussion/Storm Specific Discussion. 
                                Your job is to clearly explain what that selected text means, using context from both the original discussion and the summary.
                             
                                Write for this specific audience level: For the general public. Use simple, clear language with basic educational value. Focus on what will happen and why, without jargon. Be respectful and informative without sounding condescending.

                                An explanation should be concise.
                                Do not make any information up.
                                Maintain a consistent tone and structure as seen in the summary.

                                Only explain the selected phrase in context — don’t summarize the whole forecast.
                                
                                The original discussion and summary will be entered in the chat, make sure to use them to gain context for the selected section. \n"""
        elif self.weather_knowledge == "no_summary":
            prompt_string = """You are a meteorologist and educator. user is reading a weather forecast that was generated from an official National Weather Service Area Forecast Discussion (AFD) or NHC Tropical Weather Discussion/Storm Specific Discussion. 
                                Your job is to clearly explain what that selected text means, using context from both the original discussion and the summary.

                                Write for this specific audience level: Expert – For those with a meteorology background. Use technical terms (e.g., CAPE, shear, shortwaves, synoptic features), but if these terms are the focus of
                                of the selected text the user may need you to explain them as well.

                                An explanation should be concise.
                                Do not make any information up.
                                Maintain a consistent tone and structure as seen in the summary.

                                Only explain the selected phrase in context — don’t summarize the whole forecast.
                                
                                The original discussion will be entered in the chat, make sure to use them to gain context for the selected section. \n"""
            
            afd = """You are a meteorologist and educator. user is reading a weather forecast that was generated from an official National Weather Service Area Forecast Discussion (AFD). 
                                Your job is to clearly explain what that selected text means, using context from both the original discussion and the summary.

                                Write for this specific audience level: Expert – For those with a meteorology background. Use technical terms (e.g., CAPE, shear, shortwaves, synoptic features), but if these terms are the focus of
                                of the selected text the user may need you to explain them as well.

                                An explanation should be concise.
                                Do not make any information up.
                                Maintain a consistent tone and structure as seen in the summary.

                                Only explain the selected phrase in context — don’t summarize the whole forecast.
                                
                                The original discussion will be entered in the chat, make sure to use them to gain context for the selected section. \n"""

        afd += "\n The original Area forecast discussion is as follows: \n" + self.afd + "\n\n"

        if self.weather_knowledge != "no_summary":
            afd += "The summarized discussion is as follows: \n" + summary + "\n\n"

        afd += "The selected piece of text from the summarized discussion is what you should explain to the user at the specified level" + selected_text + "\n"

        openai.api_key = os.getenv("API_KEY") 

        # build messages datastructure 
        messages = [
            {"role": "system", "content": prompt_string},
            {"role": "user", "content": afd}
        ]
        try:
            
            response = openai.chat.completions.create(
                model="gpt-4.1-mini", 
                messages=messages,
                temperature=0.7 # make the messages a little different each time, this should hopefully allows for slightly different explanation if one doesnt click
            )
            # get reponse
            text = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            text = "There was an error generating the explanation."
        
        print(f"Expertise level: {self.weather_knowledge}, selected text: {selected_text}\n\n, Discussion: {self.afd}\n\n,  summary: {summary}")

        return text
    

    def generate_Storm_Summary(self):
        if self.weather_knowledge == "expert":
            prompt_string = """
                You are a meteorologist and educator. Your task is to write a clear, structured summary of the latest National Hurricane Center (NHC) Tropical Storm Forecast Discussion (TWD) for a specific storm. Focus on significant features, intensification trends, storm structure info, track info etc... Use technical terms appropriate for an audience with a strong meteorological background (assume a degree or strong training).

                Write for this specific audience level: Expert – For those with a meteorology background. Use technical terms (e.g., CAPE, shear, rapid intensification, synoptic/mesoscale features) and concise scientific explanations. Keep it focused and professional.

                Write 2-3 concise paragraphs.
                Explain key features, track, convection, intensification, and interactions, etc...
                Include any information about landfall times, any crucial information
                Synthesize the information; do not copy-paste.
                Do not invent information; only use the provided discussion.
                Maintain professional and scientific tone.

                The regional tropical weather discussion will be provided below.
                """
            
            afd = prompt_string + "\n\n" + self.storm_discussion
            
        elif self.weather_knowledge == "moderate":
            prompt_string = """
                You are a meteorologist and educator. Your task is to write a clear, structured summary of the latest National Hurricane Center (NHC) Tropical Storm Forecast Discussion (TWD) for a specific storm for a weather-savvy audience. Focus on significant features, intensification trends, storm structure info, track info etc... Use mostly plain language and clearly explain storms

                Write for this specific audience level: Moderate – For weather enthusiasts or TV-weather-savvy readers. Use plain language with light explanations of weather features (e.g., “a weak front will help to steer the storm…”). Include some causes and effects without overwhelming detail.

                Write 2-3 concise paragraphs.
                Explain key features, track, convection, intensification, and interactions, etc...
                Include any information about landfall times, any crucial information
                Synthesize the information; do not copy-paste.
                Do not invent information; only use the provided discussion.
                Maintain professional and scientific tone.
                If you include any advanced vocabulary, ensure to explain it

                The regional tropical weather discussion will be provided below.
                """
            
            afd = prompt_string + "\n\n" + self.storm_discussion
            
        elif self.weather_knowledge == "none":
            prompt_string = """
                You are a meteorologist and educator. Your task is to write a clear, structured summary of the latest National Hurricane Center (NHC) Tropical Storm Forecast Discussion (TWD) for a specific storm for audience with limited to no meteorological background. Focus on significant features, intensification trends, storm structure info, track info etc... Use mostly plain language and clearly explain storms.

                Write for this specific audience level: For the general public. Use simple, clear language with basic educational value. Focus on what will happen and why, without jargon. Be respectful and informative without sounding condescending. 

                Write 2-3 concise paragraphs.
                Explain key features, track, convection, intensification, and interactions, etc...
                Include any information about landfall times, any crucial information
                Synthesize the information; do not copy-paste.
                Do not invent information; only use the provided discussion.
                Maintain professional and scientific tone.
                If you include any advanced vocabulary, ensure to explain it

                The regional tropical weather discussion will be provided below.
                """
            
            afd = prompt_string + "\n\n" + self.storm_discussion
        elif self.weather_knowledge == "no_summary":
            afd = self.storm_discussion

        if self.weather_knowledge == "no_summary":
            text = afd
            text = clean_no_summary_text(text)
        else:
            # connect to openai
            openai.api_key = os.getenv("API_KEY") 

            # build messages data structure to pass to openai
            messages = [
                {"role": "system", "content": prompt_string},
                {"role": "user", "content": afd}
            ]
            try:
                # create chat message
                response = openai.chat.completions.create(
                    model="gpt-4.1-mini", 
                    messages=messages,
                    temperature=0.7
                )
                # get response
                text = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API Error: {e}")
                text = "There was an error generating the summary."
        
        return text
    
    def generate_Region_Summary(self):
        if self.weather_knowledge == "expert":
            prompt_string = """
                You are a meteorologist and educator. Your task is to write a clear, structured summary of the latest National Hurricane Center (NHC) Tropical Weather Discussion (TWD) covering an entire region. Focus on significant features, tropical waves, and large-scale weather patterns impacting the region. Use technical terms appropriate for an audience with a strong meteorological background (assume a degree or strong training).

                Write for this specific audience level: Expert – For those with a meteorology background. Use technical terms (e.g., CAPE, shear, shortwaves, synoptic/mesoscale features) and concise scientific explanations. Keep it focused and professional.

                Write 3-4 concise paragraphs.
                Explain key synoptic features, tropical waves, convection, and interactions.
                Synthesize the information; do not copy-paste.
                Do not invent information; only use the provided discussion.
                Maintain professional and scientific tone.
                Structure the summary in a similar way to the discussion. Start out with any notable features (storms, etc...) and include important information on them. Then transition into sections

                The regional tropical weather discussion will be provided below.
                """
            
            afd = prompt_string + "\n\n" + self.twd_discussion
            
        elif self.weather_knowledge == "moderate":
            prompt_string = """
                You are a meteorologist and educator. Summarize the latest National Hurricane Center (NHC) Tropical Weather Discussion (TWD) for a weather-savvy audience. Use mostly plain language and clearly explain storms, and other significant features affecting the region.

                Write for this specific audience level: Moderate – For weather enthusiasts or TV-weather-savvy readers. Use plain language with light explanations of weather features (e.g., “a weak front will help to steer the storm…”). Include some causes and effects without overwhelming detail.

                Write 3-4 concise paragraphs.
                Focus on key weather features and expected impacts.
                Synthesize the information; do not copy-paste.
                Do not invent information; only use the provided discussion.
                Maintain clear, engaging tone.
                If you include any advanced vocabulary, ensure to explain it
                Structure the summary in a similar way to the discussion. Start out with any notable features (storms, etc...) and include important information on them. Then transition into sections

                The regional tropical weather discussion will be provided below.
                """
            
            afd = prompt_string + "\n\n" + self.twd_discussion
            
        elif self.weather_knowledge == "none":
            prompt_string = """
                You are a meteorologist and educator. Summarize the latest National Hurricane Center (NHC) Tropical Weather Discussion (TWD) for an audience with limited to no meteorological background. Use mostly plain language and clearly explain storms, and other significant features affecting the region.

                Write for this specific audience level: For the general public. Use simple, clear language with basic educational value. Focus on what will happen and why, without jargon. Be respectful and informative without sounding condescending. 

                Write 2-3 concise paragraphs.
                Focus on key weather features and expected impacts.
                Synthesize the information; do not copy-paste.
                Do not invent information; only use the provided discussion.
                Maintain clear, engaging tone.
                If you include any advanced vocabulary, ensure to explain it
                Structure the summary in a similar way to the discussion. Start out with any notable features (storms, etc...) and include important information on them. Then transition into sections.
                Ignore discussion complex topics like tropical waves

                The regional tropical weather discussion will be provided below.
                """
            
            afd = prompt_string + "\n\n" + self.twd_discussion
            
        elif self.weather_knowledge == "no_summary":
            afd = self.twd_discussion

        if self.weather_knowledge == "no_summary":
            text = afd
            text = clean_no_summary_text(text)
        else:
            # connect to openai
            openai.api_key = os.getenv("API_KEY") 

            # build messages data structure to pass to openai
            messages = [
                {"role": "system", "content": prompt_string},
                {"role": "user", "content": afd}
            ]
            try:
                # create chat message
                response = openai.chat.completions.create(
                    model="gpt-4.1-mini", 
                    messages=messages,
                    temperature=0.7
                )
                # get response
                text = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API Error: {e}")
                text = "There was an error generating the summary."
        
        return text
    

def clean_no_summary_text(text):
    """
    Clean the raw afd-style text:
    - Joins lines within paragraphs.
    - Preserves paragraph breaks.
    """
    # Split into blocks based on blank lines
    paragraphs = re.split(r'\n\s*\n', text.strip())
    
    # Join wrapped lines inside each paragraph
    cleaned = [' '.join(p.strip().splitlines()) for p in paragraphs]
    
    return '\n\n'.join(cleaned)