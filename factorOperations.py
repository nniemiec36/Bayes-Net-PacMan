from bayesNet import Factor
import operator as op
import util
import functools

def joinFactorsByVariableWithCallTracking(callTrackingList=None):


    def joinFactorsByVariable(factors, joinVariable):
        """
        Input factors is a list of factors.
        Input joinVariable is the variable to join on.

        This function performs a check that the variable that is being joined on 
        appears as an unconditioned variable in only one of the input factors.

        Then, it calls your joinFactors on all of the factors in factors that 
        contain that variable.

        Returns a tuple of 
        (factors not joined, resulting factor from joinFactors)
        """

        if not (callTrackingList is None):
            callTrackingList.append(('join', joinVariable))

        currentFactorsToJoin =    [factor for factor in factors if joinVariable in factor.variablesSet()]
        currentFactorsNotToJoin = [factor for factor in factors if joinVariable not in factor.variablesSet()]

        # typecheck portion
        numVariableOnLeft = len([factor for factor in currentFactorsToJoin if joinVariable in factor.unconditionedVariables()])
        if numVariableOnLeft > 1:
            print("Factor failed joinFactorsByVariable typecheck: ", factor)
            raise ValueError("The joinBy variable can only appear in one factor as an \nunconditioned variable. \n" +  
                               "joinVariable: " + str(joinVariable) + "\n" +
                               ", ".join(map(str, [factor.unconditionedVariables() for factor in currentFactorsToJoin])))
        
        joinedFactor = joinFactors(currentFactorsToJoin)
        return currentFactorsNotToJoin, joinedFactor

    return joinFactorsByVariable

joinFactorsByVariable = joinFactorsByVariableWithCallTracking()


def joinFactors(factors):
    """
    Question 3: Your join implementation 

    Input factors is a list of factors.  
    
    You should calculate the set of unconditioned variables and conditioned 
    variables for the join of those factors.

    Return a new factor that has those variables and whose probability entries 
    are product of the corresponding rows of the input factors.

    You may assume that the variableDomainsDict for all the input 
    factors are the same, since they come from the same BayesNet.

    joinFactors will only allow unconditionedVariables to appear in 
    one input factor (so their join is well defined).

    Hint: Factor methods that take an assignmentDict as input 
    (such as getProbability and setProbability) can handle 
    assignmentDicts that assign more variables than are in that factor.

    Useful functions:
    Factor.getAllPossibleAssignmentDicts
    Factor.getProbability
    Factor.setProbability
    Factor.unconditionedVariables
    Factor.conditionedVariables
    Factor.variableDomainsDict
    """

    # typecheck portion
    setsOfUnconditioned = [set(factor.unconditionedVariables()) for factor in factors]
    if len(factors) > 1:
        intersect = functools.reduce(lambda x, y: x & y, setsOfUnconditioned)
        if len(intersect) > 0:
            print("Factor failed joinFactors typecheck: ", factor)
            raise ValueError("unconditionedVariables can only appear in one factor. \n"
                    + "unconditionedVariables: " + str(intersect) + 
                    "\nappear in more than one input factor.\n" + 
                    "Input factors: \n" +
                    "\n".join(map(str, factors)))


    "*** YOUR CODE HERE ***"
    uncond = set() # Unconditionals for the new factor
    for i in range(len(setsOfUnconditioned)):
        uncond = uncond.union(setsOfUnconditioned[i]) # get set of unconditioned variables
    setsOfConditioned = [set(factor.conditionedVariables()) for factor in factors] # Gets set of all conditioned variables
    cond_var_set=set()
    for i in range(len(setsOfConditioned)):
        cond_var_set = cond_var_set.union(setsOfConditioned[i]) # get set of conditioned variables, so that only unique values remain
    cond_var_set = cond_var_set - uncond # gets rid of values in cond set that are in uncond set

    dict = {}
    for factor in factors:
        dict = factor.variableDomainsDict()
        break

    f = Factor(uncond,cond_var_set,dict)
    # get all possible assignments in f and assign probibility based on product of the assignment for every factor
    for assignment in f.getAllPossibleAssignmentDicts():
        prob = 1
        for factor in factors:
            prob = prob * factor.getProbability(assignment)
        f.setProbability(assignment, prob)

    return f

    "*** END YOUR CODE HERE ***"


def eliminateWithCallTracking(callTrackingList=None):

    def eliminate(factor, eliminationVariable):
        """
        Question 4: Your eliminate implementation 

        Input factor is a single factor.
        Input eliminationVariable is the variable to eliminate from factor.
        eliminationVariable must be an unconditioned variable in factor.
        
        You should calculate the set of unconditioned variables and conditioned 
        variables for the factor obtained by eliminating the variable
        eliminationVariable.

        Return a new factor where all of the rows mentioning
        eliminationVariable are summed with rows that match
        assignments on the other variables.

        Useful functions:
        Factor.getAllPossibleAssignmentDicts
        Factor.getProbability
        Factor.setProbability
        Factor.unconditionedVariables
        Factor.conditionedVariables
        Factor.variableDomainsDict
        """
        # autograder tracking -- don't remove
        if not (callTrackingList is None):
            callTrackingList.append(('eliminate', eliminationVariable))

        # typecheck portion
        if eliminationVariable not in factor.unconditionedVariables():
            print("Factor failed eliminate typecheck: ", factor)
            raise ValueError("Elimination variable is not an unconditioned variable " \
                            + "in this factor\n" + 
                            "eliminationVariable: " + str(eliminationVariable) + \
                            "\nunconditionedVariables:" + str(factor.unconditionedVariables()))
        
        if len(factor.unconditionedVariables()) == 1:
            print("Factor failed eliminate typecheck: ", factor)
            raise ValueError("Factor has only one unconditioned variable, so you " \
                    + "can't eliminate \nthat variable.\n" + \
                    "eliminationVariable:" + str(eliminationVariable) + "\n" +\
                    "unconditionedVariables: " + str(factor.unconditionedVariables()))

        "*** YOUR CODE HERE ***"
        unconditioned_var = factor.unconditionedVariables()
        unconditioned_var = [var for var in unconditioned_var if var != eliminationVariable]
        conditioned_var = factor.conditionedVariables()
        domainVarDict = factor.variableDomainsDict()
        umbrella = domainVarDict[eliminationVariable]

        # we can create a new factor with the elimination variable
        new_factor = Factor(unconditioned_var, conditioned_var, domainVarDict)
        
        # for each assignment in the new factor's dict
        for x in new_factor.getAllPossibleAssignmentDicts():
            probability = 0
            # parse through the umbrella to find the elimination value
            for value in umbrella:
                # keep a copy of the value
                value_copy = x.copy()
                
                # eliminate the value
                value_copy[eliminationVariable] = value

                # calculate the probability of the value
                probability += factor.getProbability(value_copy)

            new_factor.setProbability(x, probability)
        return new_factor
        
        "*** END YOUR CODE HERE ***"

    return eliminate

eliminate = eliminateWithCallTracking()


def normalize(factor):
    """
    Question 5: Your normalize implementation 

    Input factor is a single factor.

    The set of conditioned variables for the normalized factor consists 
    of the input factor's conditioned variables as well as any of the 
    input factor's unconditioned variables with exactly one entry in their 
    domain.  Since there is only one entry in that variable's domain, we 
    can either assume it was assigned as evidence to have only one variable 
    in its domain, or it only had one entry in its domain to begin with.
    This blurs the distinction between evidence assignments and variables 
    with single value domains, but that is alright since we have to assign 
    variables that only have one value in their domain to that single value.

    Return a new factor where the sum of the all the probabilities in the table is 1.
    This should be a new factor, not a modification of this factor in place.

    If the sum of probabilities in the input factor is 0,
    you should return None.

    This is intended to be used at the end of a probabilistic inference query.
    Because of this, all variables that have more than one element in their 
    domain are assumed to be unconditioned.
    There are more general implementations of normalize, but we will only 
    implement this version.

    Useful functions:
    Factor.getAllPossibleAssignmentDicts
    Factor.getProbability
    Factor.setProbability
    Factor.unconditionedVariables
    Factor.conditionedVariables
    Factor.variableDomainsDict
    """

    # typecheck portion
    variableDomainsDict = factor.variableDomainsDict()
    for conditionedVariable in factor.conditionedVariables():
        if len(variableDomainsDict[conditionedVariable]) > 1:
            print("Factor failed normalize typecheck: ", factor)
            raise ValueError("The factor to be normalized must have only one " + \
                            "assignment of the \n" + "conditional variables, " + \
                            "so that total probability will sum to 1\n" + 
                            str(factor))

    " YOUR CODE HERE "
    uncond = factor.unconditionedVariables()
    cond = factor.conditionedVariables()
    dict = factor.variableDomainsDict()

    new_cond = cond.union(set([var for var in uncond if len(dict[var]) == 1])) # input condition + uncond vars with 1 domain
    new_uncond = set([var for var in uncond if var not in new_cond]) # uncond is input uncond except variables in new_cond
    f = Factor(new_uncond,new_cond,dict) # creates new factor that needs normalization

    sum_prob = 0 # probability sum of probabilities for all possible assignments for factor
    for assignment in factor.getAllPossibleAssignmentDicts():
        sum_prob += factor.getProbability(assignment)
    # Use sum_prob as normalization factor for new factor f
    for assignment in factor.getAllPossibleAssignmentDicts():
        prob = factor.getProbability(assignment)/sum_prob # normalize each probability
        f.setProbability(assignment,prob)

    return f
    util.raiseNotDefined()
    " END YOUR CODE HERE "
