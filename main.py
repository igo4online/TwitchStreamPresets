import tkinter as tk

from gui import TwitchPresetApp


def main():
  root=tk.Tk()

  app=TwitchPresetApp(
    root
  )

  root.mainloop()


if(__name__=="__main__"):
  main()