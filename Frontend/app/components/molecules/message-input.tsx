"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { SendIcon } from "lucide-react";
import React from "react";

interface ChatInputProps {
  submitHandler: (userInput: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ submitHandler }) => {
  const [inputValue, setInputValue] = React.useState("");
  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!inputValue.trim()) return;

    submitHandler(inputValue.trim());
    setInputValue("");
  };

  return (
    <div className="w-full flex gap-4 justify-center">
      <div className="grid w-full items-center gap-1.5">
        <form className="relative" onSubmit={handleSubmit}>
          <Textarea
            placeholder="Tanyakan Apapun Seputar Kebudayaan dan Pariwisata Bali..."
            className="w-full rounded-3xl bg-[#56411c] placeholder-[#FAF3E0] pl-3 text-[#fbfbfb] h-24 resize-none overflow-hidden"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <Button
            className="absolute right-2.5 bottom-2.5 bg-white p-4 shadow-md hover:bg-[#dedede] transition-colors duration-300"
            type="submit"
            disabled={!inputValue}
            size="icon"
          >
            <SendIcon size={100} color="black" />
          </Button>
        </form>
      </div>
    </div>
  );
};

export default ChatInput;
