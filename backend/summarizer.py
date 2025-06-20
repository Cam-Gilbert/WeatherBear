import requests
import openai
import os

class Summarizer:
    def __init__(self, weather_knowledge, afd):
        self.weather_knowledge = weather_knowledge
        self.afd = afd

    def generate_Message(self):
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

        ### Pass Message to LLM and return response if summary requested 
        if self.weather_knowledge == "no_summary":
            text = afd
        else:
            openai.api_key = os.getenv("API_KEY")  # Ensure this matches your env var name on Render

            messages = [
                {"role": "system", "content": prompt_string},
                {"role": "user", "content": afd}
            ]
            try:
                response = openai.chat.completions.create(
                    model="gpt-4.1-mini",  # or "gpt-4.0", "gpt-4.0-turbo", or whatever model you prefer
                    messages=messages,
                    temperature=0.7
                )
                text = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API Error: {e}")
                text = "There was an error generating the summary."
        

        return text

