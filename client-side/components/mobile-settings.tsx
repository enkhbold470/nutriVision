'use client'
import React from 'react'
import Image from 'next/image'
import { User, Bell, Moon, Lock, HelpCircle, LogOut } from 'lucide-react'
import { Switch } from '@/components/ui/switch'
import EG from '../public/EG.svg'
import DarkMode from "@/components/DarkMode";
import { Button } from './ui/button'
interface SettingsOption {
  icon: React.ReactNode
  label: string
  action?: () => void
  toggle?: boolean
}

export function MobileSettingsComponent() {
  const settingsOptions: SettingsOption[] = [
    { icon: <Bell className="h-5 w-5 " />, label: 'Notifications', toggle: true },
    { icon: <Lock className="h-5 w-5 " />, label: 'Privacy', action: () => console.log('Privacy settings') },
    { icon: <HelpCircle className="h-5 w-5 " />, label: 'Help & Support', action: () => console.log('Help & Support') },
    
    // { icon: <LogOut className="h-5 w-5 text-green-500" />, label: 'Log Out', action: () => console.log('Logging out') },
  ]
  return (
    <div className=" min-h-screen p-4">
          <div className='w-full flex justify-end'>

<DarkMode/>
</div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
  

      <div className=" rounded-lg shadow-md p-4 mb-6">
        <div className="flex items-center space-x-4">
          <div className="relative w-16 h-16">
                { EG ? (
                  <Image
                    src={EG}
                    alt="Profile picture"
                    layout="fill"
                    className="rounded-full"
                  />
                ) : (
                  <div className="flex items-center justify-center w-full h-full rounded-full">
                    <User className="h-8 w-8" />
                  </div>
                )}
          </div>
          <div>
            <h2 className="text-xl font-semibold ">Enkhbold Ganbold</h2>
            <p className="">enkhbold470@gmail.com</p>
          </div>
        </div>
        <button className="mt-4  font-medium" onClick={() => console.log('Edit profile')}>
          Edit Profile
        </button>
      </div>
      <div className=" rounded-lg shadow-md overflow-hidden">
        {settingsOptions.map((option, index) => (
          <div 
            key={option.label} 
            className={`flex items-center justify-between p-4 ${
              index !== settingsOptions.length - 1 ? 'border-b ' : ''
            }`}
          >
            <div className="flex items-center space-x-3">
              {option.icon}
              <span className="">{option.label}</span>
            </div>
            {option.toggle ? (
              <Switch />
            ) : (
              <Button variant="ghost" onClick={option.action} className="">
                ...
              </Button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}