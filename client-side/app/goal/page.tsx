"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
export default function Goal() {
  const [goal, setGoal] = useState("")
  const [date, setDate] = useState("")
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Here you would typically save this data to a state management solution or API
    router.push("/camera")
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4 ">Set Your Goal</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="goal" className="block text-sm font-medium ">
            Goal (e.g., lose 10 lbs)
          </label>
          <input
            type="text"
            id="goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            className="mt-1 block w-full rounded-md shadow-sm "
            required
          />
        </div>
        <div>
          <label htmlFor="date" className="block text-sm font-medium ">
            Target Date
          </label>
          <input
            type="date"
            id="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="mt-1 block w-full rounded-md  shadow-sm "
            required
          />
        </div>
        <Button
          type="submit"
          className="w-full  py-2 px-4 rounded-md hfocus:outline-none focus:ring-2  focus:ring-offset-2"
        >
          Set Goal
        </Button>
      </form>
    </div>
  )
}

