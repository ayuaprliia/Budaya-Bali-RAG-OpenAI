"use client";

import { postChat } from "@/app/actions/post-chat";
import React from "react";
import ChatBubble from "../atoms/chat-bubble";
import ChatInput from "../molecules/message-input";

type Source = {
  title: string;
  url: string;
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
    <div className="w-full h-screen flex justify-center bg-[#fffcf3]">
      <div className="w-full max-w-3xl flex flex-col justify-between h-full px-6 py-10 bg-[#fffcf3] rounded-xl">
        <div className="flex flex-col overflow-y-auto gap-8 mb-4">
          {chat.length === 0 && (
            <div className="text-center mt-50">
              <h1 className="text-[#56411c] text-3xl font-bold font-geist-sans mb-4">
                Rahajeng Semeton ❀
              </h1>
              <p className="text-lg max-w-xl mx-auto">
                Apa yang bisa saya bantu?
              </p>
            </div>
          )}

          {chat.map((chat, index) => (
            <ChatBubble
              isUser={chat.role === "user"}
              message={chat.content}
              sources={chat.sources}
              key={index}
            />
          ))}

          {isPending && (
            <ChatBubble message="Sedang membuat jawaban..." isUser={false} />
          )}
        </div>

        <div>
          <ChatInput submitHandler={handleSubmit} />
        </div>
      </div>
    </div>
  );
};

export default ChatBody;
