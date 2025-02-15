"use client";
import React from "react";
import { Home, Camera, Settings } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
const navItems = [
  { icon: Home, route: "/" },
  { icon: Camera, route: "/camera" },
  // { icon: Bell, route: "/notifications" },
  { icon: Settings, route: "/settings" },
];

const NavItem = ({
  icon: Icon,
  isActive,
  onClick,
}: {
  icon: React.ElementType;
  isActive: boolean;
  onClick: () => void;
}) => (
  <Button
  variant={isActive ? "default" : "ghost"}
    className={`p-2 rounded-full 
    ${isActive ? "bg-opacity-100" : "bg-opacity-10"}
    transition duration-300 ease-in-out transform hover:scale-105`}
    onClick={onClick}
  >
    <Icon size={30} />
  </Button>
);

export default function BottomNavbar() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("home");

  return (
    <nav className="fixed bottom-4 left-4 right-4   bg-opacity-80 backdrop-blur-md rounded-full border  border-opacity-10 shadow-xl p-2 flex justify-around">
      {navItems.map((item, index) => (
        <NavItem
          key={index}
          icon={item.icon}
          isActive={activeTab === item.route}
          onClick={() => {
            setActiveTab(item.route);
            router.push(item.route);
          }}
        />
      ))}
    </nav>
  );
}
