# Qualitative Semester Feedback through LLMs

### Ollama Configuration

```bash
ollama show --modelfile llama2
```

***Custom Configuration***

Changed values:

- temperature [0.0]: The temperature of the model. Increasing the temperature will make the model answer more creatively. (Default: 0.8)
- seed [42]: Sets the random number seed to use for generation. Setting this to a specific number will make the model generate the same text for the same prompt. (Default: 0)

***Exporting Configuration***

1. Save it as a file (e.g. Modelfile)
2. ollama create aaufeedback -f ./modelfile
3. ollama run aaufeedbackŒ
4. Start using the model!


### Preprocessing Information

**Preprocessing:**

 - Convert data format into 5 columns: campus, semeser, course, feedback_good, feedback_bad, feedback_extra 

**Model steps:** 

1. Query specific feedback
2. Concat good, bad and extra feedback into one feedback string
3. Split this feedback based upon max context length of the model
4. Summarize each split part into amount of splits done divided max model context length
5. Concat the summarized parts that now equate to the max context length of the model
6. Make the model give actionable feedback
7. Converse with the model based upon the conceited summarized text as you pleases


