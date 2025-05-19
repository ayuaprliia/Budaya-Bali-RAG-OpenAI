"use server";

export const postChat = async (question: string) => {
  try {
    const response = await fetch(`${process.env.API_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    console.log("Response from API:", response);

    if (!response.ok) {
      return { success: false, message: "Failed to generate response" };
    }

    const data = await response.json();

    return {
      success: true,
      message: "Success",
      data: {
        content: data.answer,  
        sources: data.sources, 
      },
    };
  } catch (error) {
    console.error("Error in postChat:", error);
    return { success: false, message: "Error occurred while fetching response" };
  }
};
