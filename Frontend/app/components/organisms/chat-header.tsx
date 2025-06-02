"use client";

import { UserCircle2 } from "lucide-react";

const ChatHeader = () => {
  return (
    <header className="w-full bg-[#fffcf3] py-4 px-6 shadow-md flex justify-between items-center rounded-none">
      <h1 className="text-2xl font-semibold text-[#6a4c1d]">TemanBudaya</h1>
      <div className="text-[#6a4c1d]">
        <UserCircle2 className="w-8 h-8" />
      </div>
    </header>
  );
};

export default ChatHeader;
