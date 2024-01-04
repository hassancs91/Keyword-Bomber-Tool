import requests
import httpx
import xml.etree.ElementTree as ET
import prompts
import llm

LLM_MODEL = "gpt-3.5-turbo-1106"

async def get_keyword_data(input_keyword, input_country,api_key):
    # Get results
    keyword_data = await get_suggestion_keywords_google_optimized(
        input_keyword, input_country
    )

    ai_report = await suggestions_ai_analysis(keyword_data,api_key)

    # Preparing the result
    result = {
        "success": True,
        "message": "Success! Keywords Generated",
        "result": {
            "ai_report": ai_report,
            "keyword_data": keyword_data,
        },
    }

    # Print the result
    print(result)

    return result

async def suggestions_ai_analysis(keyword_data: str, api_key):
    max_retries = 5

    for _ in range(max_retries):
        try:
            # Get Json Structure
            prompt = prompts.suggestion_keywords_analysis.format(
                KEYWORD_DATA=keyword_data
            )

            return await llm.generate_response(prompt, LLM_MODEL, api_key)

        except Exception as e:
            print(
                f"Failed to generate analysis for suggestion keywords. Exception type: {type(e).__name__}, Message: {str(e)}"
            )

    return ""



async def get_suggestion_keywords_google_optimized(query, countryCode):
    # Define categorization keywords for all categories
            categories = {
                "Questions": ["who", "what", "where", "when", "why", "how", "are"],
                "Prepositions": ["can", "with", "for"],
                "Alphabit": list("abcdefghijklmnopqrstuvwxyz"),
                "Comparisons": ["vs", "versus", "or"],
                "Intent-Based": ["buy", "review", "price", "best", "top", "how to", "why to"],
                "Time-Related": ["when", "schedule", "deadline", "today", "now", "latest"],
                "Audience-Specific": ["for beginners", "for small businesses", "for students", "for professionals"],
                "Problem-Solving": ["solution", "issue", "error", "troubleshoot", "fix"],
                "Feature-Specific": ["with video", "with images", "analytics", "tools", "with example"],
                "Opinions/Reviews": ["review", "opinion", "rating", "feedback", "testimonial"],
                "Cost-Related": ["price", "cost", "budget", "cheap", "expensive", "value"],
                "Trend-Based": ["trends", "new", "upcoming"]
            }

            categorized_suggestions = {key: {} for key in categories.keys()}

            for category in categories:
                for keyword in categories[category]:
                    try:
                        if category in ["Questions", "Prepositions", "Intent-Based", "Time-Related",
                                    "Audience-Specific", "Problem-Solving", "Opinions/Reviews", "Cost-Related", "Trend-Based"]:
                            modified_query = f"{keyword} {query}"
                        elif category in ["Alphabit", "Feature-Specific", "Industry-Specific"]:
                            modified_query = f"{query} {keyword}"
                        else:
                            # Default pattern if not specified above
                            modified_query = f"{keyword} {query}"

                        category_suggestions = await get_suggestions_for_query_async(modified_query,countryCode)
                        categorized_suggestions[category][keyword] = category_suggestions
                    except Exception as e:
                        print (f"Error in get_suggestion_keywords_google_optimized, {e}")
            return categorized_suggestions

async def get_suggestions_for_query_async(query,country):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://google.com/complete/search?output=toolbar&gl={country}&q={query}")
            suggestions = []
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for complete_suggestion in root.findall('CompleteSuggestion'):
                    suggestion_element = complete_suggestion.find('suggestion')
                    if suggestion_element is not None:
                        data = suggestion_element.get('data').lower()
                        suggestions.append(data)
        except Exception as e:
            #nothing
            error = e

        return suggestions

def get_suggestions_for_query(query):
    response = requests.get(f"http://google.com/complete/search?output=toolbar&q={query}")
    suggestions = []
    try:
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for complete_suggestion in root.findall('CompleteSuggestion'):
                suggestion_element = complete_suggestion.find('suggestion')
                if suggestion_element is not None:
                    data = suggestion_element.get('data').lower()
                    suggestions.append(data)
    except Exception as e:
        print(
                f"keyword_research: get_suggestions_for_query. Exception type: {type(e).__name__}, Message: {str(e)}"
            )
    return suggestions