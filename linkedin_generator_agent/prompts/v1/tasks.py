RESEARCH_TASK = """Analyze research data and extract key insights fior a linkedin post
Topic:{topic}
Post Type :{post_type}
Research Data : {research_data}


Extract and return JSON:
{{
    "key_facts":["6-7 compelling statistics and facts"],
    "trending_angles":["3-5 fresh angles or framings for the topic"],
    "credible_sources":["sources that can be referenced"],
    "hook_opportunity":["potential opening line based on hook research"]
}}

Focus on recent, credible information that supports engaging content creation"""


WRITING_TASK = """Create an engaging linkedinm post based on research insights
Topic:{topic}
Tone:{tone}
Post Type : {post_type}
Research Insights : {research_insights}

POST STRUCTURE GUIDELINES:
- Story: Hook -> Personal anecdote -> Lesson -> CTA
- Hot Take : Contrarian hook -> Reasoining -> Invite Discussion
- Annoucement : News -> Why it matters -> Next Steps
- Lesson Learned : Challenge -> What happened -> Takeaways

Linkedin's Best practises:
1. Start with a strong first line to grab attention.
2.Keep the post clear and concise.
3.Use short paragraphs or bullet points for easy reading.
4.Share useful, relevant, or thoughtful content.
5.Use a natural, authentic tone.
6.Add one clear idea per post.
7.Include a question or call to action at the end.
8.Add a few relevant hashtags, but don’t overdo it.
9.Engage with comments after posting.
10.Avoid making the post too promotional.
11.Check spelling, grammar, and formatting before posting.

RETURN JSON:
{{
    "post_content":"complete linkedin post",
    "hook":"first line expected",
    "word_count":"number",
    "facts_used":["research points incorporated"]
}}"""

VALIDATION_TASK = """"""