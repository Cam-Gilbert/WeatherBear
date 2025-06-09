class summarizer:
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
                                Maintain a consistent tone and structure.

                                Here is the AFD text to summarize:\n"""
            prompt_string = prompt_string + self.afd
            
        elif self.weather_knowledge == "moderate":
            prompt_string = """You are a meteorologist and educator. Your task is to write a clear, structured weather summary for a general audience based on the latest NWS Area Forecast Discussion (AFD). Your summary should explain what the weather will be and what is causing it, with a focus on today, tonight, and tomorrow. You may briefly mention days 2-4 only if significant weather is forecast. 
                                
                                Write for this specific audience level: Moderate – For weather enthusiasts or TV-weather-savvy readers. Use plain language with light explanations of weather features (e.g., “a weak front will bring…”). Include some causes and effects without overwhelming detail.

                                Each version should be 1-2 concise paragraphs.
                                Always explain key features driving the weather (e.g., fronts, upper-level disturbances, instability, etc.).
                                Do not copy and paste from the AFD—synthesize and explain.
                                Avoid long lists of temperatures or chance-of-rain percentages.
                                Maintain a consistent tone and structure.

                                Here is the AFD text to summarize:\n"""
            prompt_string = prompt_string + self.afd
        elif self.weather_knowledge == "none":
            prompt_string = """You are a meteorologist and educator. Your task is to write a clear, structured weather summary for a general audience based on the latest NWS Area Forecast Discussion (AFD). Your summary should explain what the weather will be and what is causing it, with a focus on today, tonight, and tomorrow. You may briefly mention days 2-4 only if significant weather is forecast. 
                                
                                Write for this specific audience level: For the general public. Use simple, clear language with basic educational value. Focus on what will happen and why, without jargon. Be respectful and informative without sounding condescending.

                                Each version should be 1-2 concise paragraphs.
                                Attempt to explain key features driving the weather (e.g., fronts, upper-level disturbances, instability, etc.).
                                Do not copy and paste from the AFD—synthesize and explain.
                                Avoid long lists of temperatures or chance-of-rain percentages.
                                Maintain a consistent tone and structure.

                                Here is the AFD text to summarize:\n"""
            prompt_string = prompt_string + self.afd


        ### Pass Message to LLM and return response