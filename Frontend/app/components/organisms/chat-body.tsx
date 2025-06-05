"use client";

import { postChat } from "@/app/actions/post-chat";
import React from "react";
import ChatBubble from "../atoms/chat-bubble";
import ChatInput from "../molecules/message-input";
import ChatHeader from "./chat-header";

type Source = {
  title: string;
  url: string;
  image?: string;
};

type MessageProps = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

const ChatBody = () => {
  const [chat, setChat] = React.useState<MessageProps[]>([]);
  const [isPending, startTransition] = React.useTransition();

  const handleMessage = (message: MessageProps) => {
    setChat((prev) => [...prev, message]);
  };

  const handleSubmit = (input: string) => {
    const userMessage: MessageProps = { role: "user", content: input };
    handleMessage(userMessage);

    startTransition(async () => {
      const response = await postChat(input);
      if (response.success && response.data) {
        handleMessage({
          role: "assistant",
          content: response.data.content!,
          sources: response.data.sources,
        });
      } else {
        handleMessage({
          role: "assistant",
          content: "Maaf, terjadi kesalahan.",
        });
      }
    });
  };

  return (
    <div className="flex flex-col h-screen bg-[#fffcf3]">
      <ChatHeader />

      <div className="flex-grow overflow-y-auto px-6 py-4 max-w-3xl w-full mx-auto">
        {chat.length === 0 ? (
          <div className="text-center mt-40 text-[#56411c]">
            <h1 className="text-3xl font-bold font-geist-sans mb-4">Rahajeng Semeton ❀</h1>
            <p className="text-lg max-w-xl mx-auto mb-10">Apa yang bisa saya bantu?</p>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            {chat.map((chat, index) => (
              <React.Fragment key={index}>
                <ChatBubble
                  isUser={chat.role === "user"}
                  message={chat.content}
                  sources={chat.role === "assistant" ? chat.sources : undefined}
                />

                {chat.role === "assistant" && chat.sources && chat.sources.length > 0 && (
                  <div className="flex flex-col gap-4">
                    {chat.sources.map((src, imgIndex) =>
                      src.image ? (
                        <div key={imgIndex} className="w-full flex justify-start">
                          <div className="w-fit max-w-xs rounded-xl overflow-hidden shadow-md border border-gray-300">
                            <img
                              src={src.image}
                              alt={src.title}
                              className="w-full h-auto object-cover"
                            />
                          </div>
                        </div>
                      ) : null
                    )}
                  </div>
                )}
              </React.Fragment>
            ))}

            {isPending && <ChatBubble message="Sedang menyiapkan jawaban..." isUser={false} />}
          </div>
        )}
      </div>

      <div className="w-full max-w-3xl mx-auto px-6 py-4 bg-[#fffcf6] rounded-t-xl">
        <ChatInput submitHandler={handleSubmit} />
      </div>
    </div>
  );
};

export default ChatBody;